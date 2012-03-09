import shlex
from twisted.internet import reactor
from twisted.internet.interfaces import IProcessProtocol
from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.web.http import Request
from gitdaemon import Application
from gitdaemon.git import findGitShell, findGitHTTPBackend
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler, IRepositoryRouter
from gitdaemon.protocol.authorization import AuthorizedProcessProtocolWrapper

class StubInvocationRequest(object):
    implements(IInvocationRequest)

    def __init__(self, request, proto, user, env = {}, args = []):
        self.proto = proto
        self.user = user
        self.env = env
        self.args = args
        self.repoPath = []

    def getProtocol(self):
        return self.proto

    def getRepositoryPath(self):
        return self.repoPath

    def getUser(self):
        return self.user

    def invocate(self, repository):
        pass

class StubInvocationRequestHandler(object):
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    def handle(self, app, request):
        request.invocate(None)

    def createHTTPInvocationRequest(self, request, proto, user, env, qargs = {}):
        request = StubInvocationRequest(request, proto, user, env, qargs)

        return request

    def createSSHInvocationRequest(self, request, proto, user):
        request = StubInvocationRequest(request, proto, user)

        return request

stubInvocationRequestHandler = StubInvocationRequestHandler()

from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from zope.interface.interface import Interface
from gitdaemon.interfaces import IAuth

class IUserStub(Interface):
    """Stub for User class"""

class UserStub(object):
    implements(IUserStub)

class Auth(object):
    implements(IPlugin, IAuth)

    UserInterface = IUserStub

    def allowAnonymousAccess(self, app):
        return defer.succeed(UserStub())

    def authenticateKey(self, app, credentials):
        assert ISSHPrivateKey.providedBy(credentials)

        return defer.succeed(UserStub())

    def authenticatePassword(self, app, credentials):
        assert IUsernamePassword.providedBy(credentials)

        if credentials.username == "git":
            return defer.succeed(UserStub())
        else:
            return None

    def mayAccess(self, app, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return True

auth = Auth()