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

    UserInterface = None

    def allowAnonymousAccess(self):
        return UserStub()

    def authenticateKey(self, key, credentials):
        return UserStub()

    def authenticatePassword(self, user, password):
        if user == "git":
            return UserStub()
        else:
            return None

    def mayAccess(self, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return True

auth = Auth()