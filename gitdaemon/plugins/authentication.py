from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IAuthentication

class Authentication(object):
    implements(IPlugin, IAuthentication)

    def authenticateKey(self, key, credentials):
        return True

    def authenticatePassword(self, user, password):
        return True

authentication = Authentication()