import shlex
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from twisted.internet.interfaces import IProcessProtocol
from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.web.http import Request
from zope.interface.interface import Interface
from gitdaemon import Application
from gitdaemon.error import UserException, GitUserException
from gitdaemon.git import findGitShell, findGitHTTPBackend
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler, IRepositoryRouter
from gitdaemon.protocol.authorization import AuthorizedProcessProtocolWrapper

class InvocationRequest(object):

    def __init__(self, proto, user, env = {}, args = []):
        assert isinstance(proto, ProcessProtocol)

        #self.proto = AuthorizedProcessProtocolWrapper(proto)
        self.proto = proto
        self.user = user
        self.env = env
        self.args = args
        self.repoPath = []

        self._invariant()

    def getProtocol(self):
        self._invariant()

        return self.proto
    
    def getRepositoryPath(self):
        self._invariant()

        return self.repoPath

    def getUser(self):
        self._invariant()

        return self.user

    def _invariant(self):
        assert IProcessProtocol.providedBy(self.proto)
        assert isinstance(self.repoPath, list)
        assert isinstance(self.env, dict)
        assert isinstance(self.args, list)

class HTTPInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    gitHTTPBackend = findGitHTTPBackend()

    def __init__(self, request, proto, user, env = {}, args = []):
        assert isinstance(request, Request)

        self.request = request
        InvocationRequest.__init__(self, proto, user, env, args);
        self.repoPath = request.prepath[:-1]
        self._invariant()

    def invocate(self, repository):
        assert isinstance(repository, str)

        self._invariant()

        self.env['SCRIPT_FILENAME'] = self.gitHTTPBackend
        self.env['GIT_PROJECT_ROOT'] = repository
        self.env['PATH_INFO'] = "/" + "/".join(self.request.prepath[-1:])
        self.env['REMOTE_USER'] = 'christophe'
        self.env['GIT_HTTP_EXPORT_ALL'] = '1'

        reactor.spawnProcess(self.proto, self.gitHTTPBackend, [self.gitHTTPBackend] + self.args, self.env)

        self._invariant()

    def _invariant(self):
        InvocationRequest._invariant(self)
        assert isinstance(self.request, Request)

class SSHInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    gitShell = findGitShell()

    def __init__(self, request, proto, user, env = {}, args = []):
        argv = shlex.split(request)
        self.command = argv[0]
        InvocationRequest.__init__(self, proto, user, env, args);
        self.repoPath = argv[-1].split('/')
        self._invariant()

    def invocate(self, repository):
        assert isinstance(repository, str)

        self._invariant()

        env = {}
        command = self.command + ' ' + "'{0}'".format(repository)

        reactor.spawnProcess(self.proto, self.gitShell, (self.gitShell, '-c', command), env)

        self._invariant()

    def _invariant(self):
        InvocationRequest._invariant(self)
        assert isinstance(self.command, str)

class InvocationRequestHandler(object):
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    def _authorizationCallback(self, result, app, request, repository):
        assert isinstance(result, bool)
        assert isinstance(app, Application)
        assert IInvocationRequest.providedBy(request)

        """Callback for the dereferred returned by the authorization subsystem."""

        if result:
            request.invocate(repository)
        else:
            app.getErrorHandler().handle(GitUserException("You don't have access to this repository.", True, request.getProtocol()))

    def handle(self, app, request):
        assert isinstance(app, Application)
        assert IInvocationRequest.providedBy(request)

        repository = app.getRepositoryRouter().route(app, request.getRepositoryPath())

        if repository is not None:
            # mayAccess can return a deferred that returns a value or just return a value
            # many authorization requests go to another subsystem first

            # TODO If the AuthorizationProtocol wrapper is completed, integrate it more in the Request objects
            # TODO so we can extract a list of labels the request affects.
            d = maybeDeferred(app.getAuth().mayAccess, app, request.getUser(), repository, False)

            d.addCallback(self._authorizationCallback, app, request, repository)
        else:
            app.getErrorHandler().handle(GitUserException("The specified repository doesn't exist.", True, request.getProtocol()))

    def createHTTPInvocationRequest(self, request, proto, user, env, qargs = {}):
        assert(isinstance(request, Request))
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(env, dict))
        assert(isinstance(qargs, list) or isinstance(qargs, str))

        request = HTTPInvocationRequest(request, proto, user, env, qargs)

        assert(isinstance(request, InvocationRequest))

        return request

    def createSSHInvocationRequest(self, request, proto, user):
        assert(isinstance(request, str))
        assert(isinstance(proto, ProcessProtocol))

        request = SSHInvocationRequest(request, proto, user)

        assert(isinstance(request, InvocationRequest))

        return request

invocationRequestHandler = InvocationRequestHandler()