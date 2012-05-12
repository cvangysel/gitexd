import shlex
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from twisted.internet.interfaces import IProcessProtocol
from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
import twisted
from gitexd import Factory, Object
from gitexd.protocol.git import UnexistingRepositoryException, getGit
from zope.interface import implements
from gitexd.interfaces import IRequest, IRequestHandler
from gitexd.protocol import ssh, http, PUSH, PULL, authorization
from gitexd.protocol.authorization import  UnauthorizedRepositoryException, UnauthorizedReferencesException

class Request(Object):

    GIT = getGit()

    def __init__(self, app, request, repositoryPath, protocol, session, environmentVariables = {}):
        self._request = request
        self._repositoryPath = repositoryPath
        self._protocol = protocol
        self._authenticationSession = session
        self._environmentVariables = environmentVariables

        Object.__init__(self, app)

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
        Object._invariant(self)
        assert IProcessProtocol.providedBy(self._protocol)
        assert isinstance(self._repositoryPath, list)
        assert isinstance(self._environmentVariables, dict)
        assert self.getType() in (PUSH, PULL)

    def _labelAuthorizationCallback(self, request, protocol):
        from gitexd.protocol import GitProcessProtocol
        assert isinstance(protocol, GitProcessProtocol)
        assert request[-1] is None

        type = self.getType()
        labels = map(lambda x: x.split(), request[:-1])

        assert isinstance(labels, list)
        assert not labels or (reduce(lambda acc, x: acc and (x[0] in ("want", "have")), labels) and type == PULL) or type == PUSH

        def _callback(result):
            if result:
                protocol.authorize()
            else:
                return Failure(UnauthorizedReferencesException())

        d = maybeDeferred(self.app.getAuth().authorizeReferences, self.getSession(), labels, self.getType())
        d.addCallback(_callback)
        d.addErrback(authorization.authorizationErrorHandler, self.app, self.getProtocol())

class HTTPRequest(Request):
    implements(IRequest)

    def __init__(self, app, request, protocol, session, environmentVariables = {}):
        assert isinstance(request, twisted.web.http.Request)
        assert isinstance(protocol, ProcessProtocol)

        protocol = http.GitProcessProtocol(protocol, self._labelAuthorizationCallback)
        repositoryPath = request.prepath[:-1]

        Request.__init__(self, app, request, repositoryPath, protocol, session, environmentVariables)

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
        return PUSH if self._request.prepath[-1] == "git-receive-pack" else PULL

    def _invariant(self):
        Request._invariant(self)
        assert isinstance(self._request, twisted.web.http.Request)

class SSHRequest(Request):
    implements(IRequest)

    def __init__(self, app, request, protocol, session):
        assert isinstance(protocol, ProcessProtocol)

        request = shlex.split(request)
        repositoryPath = filter(None, request[-1].split('/'))
        protocol = ssh.GitProcessProtocol(protocol, self._labelAuthorizationCallback)

        Request.__init__(self, app, request, repositoryPath, protocol, session)

        self._invariant()

    def finish(self, repository):
        assert isinstance(repository, str)
        self._invariant()

        command = self._request[0] + " '{0}'".format(repository)
        process = reactor.spawnProcess(self._protocol, self.GIT, (self.GIT, 'shell', '-c', command), self._environmentVariables)

        self._invariant()

    def getType(self):
        return PUSH if self._request[0] == "git-receive-pack" else PULL

    def _invariant(self):
        Request._invariant(self)
        assert isinstance(self._request, list)

class RequestHandler(object):
    implements(IPlugin, IRequestHandler)

    """The main invocation logic when handling a Git request"""

    def _authorizationCallback(self, result, app, request, repository):
        assert isinstance(result, bool)
        assert isinstance(app, Factory)
        assert IRequest.providedBy(request)

        """Callback for the dereferred returned by the authorization subsystem."""

        if result:
            request.finish(repository)
        else:
            app.getErrorHandler().handle(UnauthorizedRepositoryException(request.getProtocol()))

    def handle(self, app, request):
        assert isinstance(app, Factory)
        assert IRequest.providedBy(request)

        repository = app.getRepositoryRouter().route(app, request.getRepositoryPath())

        if repository is not None:
            # authorizeRepository can return a deferred that returns a value or just return a value
            # many authorization requests go to another subsystem first

            d = maybeDeferred(app.getAuth().authorizeRepository, request.getSession(), repository, request.getType())
            d.addCallback(self._authorizationCallback, app, request, repository)
            d.addErrback(authorization.authorizationErrorHandler, app, request.getProtocol())
        else:
            app.getErrorHandler().handle(UnexistingRepositoryException(request.getProtocol()))

    def createHTTPRequest(self, app, request, proto, user, env):
        assert(isinstance(request, twisted.web.http.Request))
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(env, dict))

        request = HTTPRequest(app, request, proto, user, env)

        assert(isinstance(request, Request))

        return request

    def createSSHRequest(self, app, request, proto, user):
        assert(isinstance(request, str))
        assert(isinstance(proto, ProcessProtocol))

        request = SSHRequest(app, request, proto, user)

        assert(isinstance(request, Request))

        return request

invocationRequestHandler = RequestHandler()