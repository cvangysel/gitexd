from twisted.plugin import IPlugin
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler

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

    def finish(self, repository):
        pass

class StubInvocationRequestHandler(object):
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    def handle(self, app, request):
        request.finish(None)

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

    def authorizeRepository(self, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return True

auth = Auth()