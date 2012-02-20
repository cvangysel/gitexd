from twisted.cred.credentials import IUsernamePassword, ISSHPrivateKey
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IAuth
from gitdaemon.tests.plugins.default.default import UserStub, IUserStub

class Auth(object):
    implements(IPlugin, IAuth)

    UserInterface = IUserStub

    def allowAnonymousAccess(self):
        return defer.succeed(UserStub())

    def authenticateKey(self, credentials):
        assert ISSHPrivateKey.providedBy(credentials)

        if credentials.username == "key":
            return defer.succeed(UserStub())
        else:
            return None

    def authenticatePassword(self, credentials):
        assert IUsernamePassword.providedBy(credentials)

        return None

    def mayAccess(self, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return True

auth = Auth()