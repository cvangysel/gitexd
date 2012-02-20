from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IAuth

class Auth(object):
    implements(IPlugin, IAuth)

    """Trivial implementation of the auth plugin that doesn't check anything."""

    UserInterface = None

    def allowAnonymousAccess(self):
        return defer.succeed(True)

    def authenticateKey(self, credentials):
        assert ISSHPrivateKey.providedBy(credentials)

        return defer.succeed(True)

    def authenticatePassword(self, credentials):
        assert IUsernamePassword.providedBy(credentials)

        return defer.succeed(True)

    def mayAccess(self, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return True

auth = Auth()