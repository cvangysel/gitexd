import shlex
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from twisted.internet.interfaces import IProcessProtocol
from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
from twisted.web.http import Request
from gitdaemon import Application
from gitdaemon.protocol.error import  GitError
from gitdaemon.protocol.git import UnexistingRepositoryException, getGit
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler
from gitdaemon.protocol import ssh, http
from gitdaemon.protocol.authorization import  UnauthorizedException

class InvocationRequest(object):

    git = getGit()

    def __init__(self, proto, user, env = {}):
        self.user = user
        self.env = env
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

class HTTPInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    def __init__(self, request, proto, user, env = {}):
        assert isinstance(request, Request)
        assert isinstance(proto, ProcessProtocol)

        self.proto = http.GitProcessProtocol(proto)

        self.request = request
        InvocationRequest.__init__(self, proto, user, env)
        self.repoPath = request.prepath[:-1]
        self._invariant()

    def invocate(self, repository):
        assert isinstance(repository, str)

        self._invariant()

        # TODO Fix this, especially the REMOTE_USER env var
        self.env['SCRIPT_FILENAME'] = self.git

        self.env['GIT_PROJECT_ROOT'] = repository
        self.env['PATH_INFO'] = "/" + "/".join(self.request.prepath[-1:])

        self.env['REMOTE_USER'] = str(self.user)

        self.env['GIT_HTTP_EXPORT_ALL'] = '1'

        reactor.spawnProcess(self.proto, self.git, (self.git, 'http-backend'), self.env)

        self._invariant()

    def _invariant(self):
        InvocationRequest._invariant(self)
        assert isinstance(self.request, Request)

class SSHInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    def __init__(self, request, proto, user):
        assert isinstance(proto, ProcessProtocol)

        self.proto = ssh.GitProcessProtocol(proto)

        argv = shlex.split(request)
        self.command = argv[0]
        InvocationRequest.__init__(self, proto, user);
        self.repoPath = filter(None, argv[-1].split('/'))
        self._invariant()

    def invocate(self, repository):
        assert isinstance(repository, str)

        self._invariant()

        env = {}
        command = self.command + ' ' + "'{0}'".format(repository)

        reactor.spawnProcess(self.proto, self.git, (self.git, 'shell', '-c', command), env)

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
            app.getErrorHandler().handle(UnauthorizedException("You don't have access to this repository."))

    def _errorHandler(self, fail, app, proto):
        #TODO Fix this; also look at authentication stuff

        assert isinstance(fail, Failure)
        assert isinstance(app, Application)
        assert IProcessProtocol.providedBy(proto)

        r = fail.trap(GitError, NotImplementedError, Exception)

        if r == GitError:
            """Pass to the ExceptionHandler"""

            app.getErrorHandler().handle(fail.value, proto)
        elif r == NotImplementedError:
            """Unknown exception, halt excecution"""

            fail.printTraceback()
            reactor.stop()
        else:
            reactor.stop()

    def handle(self, app, request):
        assert isinstance(app, Application)
        assert IInvocationRequest.providedBy(request)

        repository = app.getRepositoryRouter().route(app, request.getRepositoryPath())

        if repository is not None:
            # mayAccess can return a deferred that returns a value or just return a value
            # many authorization requests go to another subsystem first

            # TODO If the AuthorizationProtocol wrapper is completed, integrate it more in the Request objects
            # TODO so we can extract a list of labels the request affects.
            d = maybeDeferred(app.getAuth().authorizeRepository, app, request.getUser(), repository, False)

            d.addCallback(self._authorizationCallback, app, request, repository)

            d.addErrback(self._errorHandler, app, request.getProtocol())
        else:
            app.getErrorHandler().handle(UnexistingRepositoryException(request.getProtocol()))

    def createHTTPInvocationRequest(self, request, proto, user, env):
        assert(isinstance(request, Request))
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(env, dict))

        request = HTTPInvocationRequest(request, proto, user, env)

        assert(isinstance(request, InvocationRequest))

        return request

    def createSSHInvocationRequest(self, request, proto, user):
        assert(isinstance(request, str))
        assert(isinstance(proto, ProcessProtocol))

        request = SSHInvocationRequest(request, proto, user)

        assert(isinstance(request, InvocationRequest))

        return request

invocationRequestHandler = InvocationRequestHandler()