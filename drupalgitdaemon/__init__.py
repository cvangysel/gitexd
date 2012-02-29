from zope.interface.declarations import implements
from zope.interface.interface import Interface

class IUser(Interface):
    """ """

    def mayRead(self, label = None):
        """ """

    def mayWrite(self, label = None):
        """ """

class User(object):
    implements(IUser)

class AnonymousUser(object):
    implements(IUser)