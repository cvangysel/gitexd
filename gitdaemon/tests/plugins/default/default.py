from twisted.plugin import IPlugin
from zope.interface import implements
from gitdaemon.interfaces import IRequest, IRequestHandler

class StubRequest(object):
    implements(IRequest)

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

class StubRequestHandler(object):
    implements(IPlugin, IRequestHandler)

    """The main invocation logic when handling a Git request"""

    def handle(self, app, request):
        request.finish(None)

    def createHTTPRequest(self, request, proto, user, env, qargs = {}):
        request = StubRequest(request, proto, user, env, qargs)

        return request

    def createSSHRequest(self, request, proto, user):
        request = StubRequest(request, proto, user)

        return request

stubInvocationRequestHandler = StubRequestHandler()

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

    def authorizeRepository(self, user, repository, requestType):
        return True

    def authorizeReferences(self, session, refs, requestType):
        return True

auth = Auth()