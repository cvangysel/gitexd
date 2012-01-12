from twisted.conch.interfaces import IConchUser
from twisted.cred import portal
from twisted.web.resource import IResource
from zope.interface.declarations import implements
from gitdaemon import Object
from gitdaemon.protocol.http import GitHTTP
from gitdaemon.protocol.ssh import GitConchUser
from gitdaemon.shared.user import User

class Realm(Object):
    implements(portal.IRealm)

    def __init__(self, app):
        Object.__init__(self, app)

    def requestAvatar(self, username, mind, *interfaces):
        if IConchUser in interfaces:
            return IConchUser, GitConchUser(self.app, username), lambda: None
        elif IResource in interfaces:
            return IResource, GitHTTP(self.app, User(username)), lambda: None
        else:
            raise NotImplementedError()