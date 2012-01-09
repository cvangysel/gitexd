from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IAuth

class Auth(object):
    implements(IPlugin, IAuth)

    def allowAnonymousAccess(self):
        print "allowAnon?"
        return False

    def authenticateKey(self, key, credentials):
        return True

    def authenticatePassword(self, user, password):
        return True

    def mayAccess(self, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        print "Got Authentication request"

        return True

auth = Auth()