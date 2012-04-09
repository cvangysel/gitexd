import shlex
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from twisted.internet.interfaces import IProcessProtocol
from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.web.http import Request
from gitdaemon import Application
from gitdaemon.protocol.git import UnexistingRepositoryException, getGit
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler
from gitdaemon.protocol import ssh, http, PUSH, PULL, authorization
from gitdaemon.protocol.authorization import  UnauthorizedException

class InvocationRequest(object):

    GIT = getGit()

    def __init__(self, request, repositoryPath, protocol, session, environmentVariables = {}):
        self._request = request
        self._repositoryPath = repositoryPath
        self._protocol = protocol
        self._authenticationSession = session
        self._environmentVariables = environmentVariables

        self._invariant()

    def getProtocol(self):
        self._invariant()

        return self._protocol
    
    def getRepositoryPath(self):
        self._invariant()

        return self._repositoryPath

    def getSession(self):
        self._invariant()

        return self._authenticationSession

    def getType(self):
        # Assume dumb version of protocol (read-only)
        return PULL

    def _invariant(self):
        assert IProcessProtocol.providedBy(self._protocol)
        assert isinstance(self._repositoryPath, list)
        assert isinstance(self._environmentVariables, dict)
        assert self.getType() in (PUSH, PULL)

class HTTPInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    def __init__(self, request, protocol, session, environmentVariables = {}):
        assert isinstance(request, Request)
        assert isinstance(protocol, ProcessProtocol)

        protocol = http.GitProcessProtocol(protocol)
        repositoryPath = request.prepath[:-1]

        InvocationRequest.__init__(self, request, repositoryPath, protocol, session, environmentVariables)

        self._invariant()

    def finish(self, repository):
        assert isinstance(repository, str)

        self._invariant()

        self._environmentVariables['SCRIPT_FILENAME'] = self.GIT
        self._environmentVariables['GIT_PROJECT_ROOT'] = repository
        self._environmentVariables['PATH_INFO'] = "/" + "/".join(self._request.prepath[-1:])
        self._environmentVariables['REMOTE_USER'] = str(self._authenticationSession)
        self._environmentVariables['GIT_HTTP_EXPORT_ALL'] = '1'

        reactor.spawnProcess(self._protocol, self.GIT, (self.GIT, 'http-backend'), self._environmentVariables)

        self._invariant()

    def getType(self):
        return PUSH if self._request.prepath[-1:] == "git-receive-pack" else PULL

    def _invariant(self):
        InvocationRequest._invariant(self)
        assert isinstance(self._request, Request)

class SSHInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    def __init__(self, request, protocol, session):
        assert isinstance(protocol, ProcessProtocol)

        request = shlex.split(request)
        repositoryPath = filter(None, request[-1].split('/'))
        protocol = ssh.GitProcessProtocol(protocol)

        InvocationRequest.__init__(self, request, repositoryPath, protocol, session)

        self._invariant()

    def finish(self, repository):
        assert isinstance(repository, str)
        self._invariant()

        command = self._request[0] + " '{0}'".format(repository)

        reactor.spawnProcess(self._protocol, self.GIT, (self.GIT, 'shell', '-c', command), self._environmentVariables)

        self._invariant()

    def getType(self):
        return PUSH if self._request[0] == "git-receive-pack" else PULL

    def _invariant(self):
        InvocationRequest._invariant(self)
        assert isinstance(self._request, list)

class InvocationRequestHandler(object):
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    def _authorizationCallback(self, result, app, request, repository):
        assert isinstance(result, bool)
        assert isinstance(app, Application)
        assert IInvocationRequest.providedBy(request)

        """Callback for the dereferred returned by the authorization subsystem."""

        if result:
            request.finish(repository)
        else:
            app.getErrorHandler().handle(UnauthorizedException("You don't have access to this repository."))

    def handle(self, app, request):
        assert isinstance(app, Application)
        assert IInvocationRequest.providedBy(request)

        repository = app.getRepositoryRouter().route(app, request.getRepositoryPath())

        if repository is not None:
            # authorizeRepository can return a deferred that returns a value or just return a value
            # many authorization requests go to another subsystem first

            d = maybeDeferred(app.getAuth().authorizeRepository, request.getSession(), repository, request.getType())
            d.addCallback(self._authorizationCallback, app, request, repository)
            d.addErrback(authorization.authorizationErrorHandler, app, request.getProtocol())
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