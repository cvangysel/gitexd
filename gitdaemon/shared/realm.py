from twisted.conch.interfaces import IConchUser
from twisted.cred import portal
from twisted.web.resource import IResource
from zope.interface.declarations import implements
from gitdaemon.protocol.http import GitHTTP
from gitdaemon.protocol.ssh import GitConchUser
from gitdaemon.shared.user import User

class Realm:
    implements(portal.IRealm)

    def __init__(self, requestHandler):
        self.requestHandler = requestHandler

    def requestAvatar(self, username, mind, *interfaces):
        if IConchUser in interfaces:
            return IConchUser, GitConchUser(username, self.requestHandler), lambda: None
        elif IResource in interfaces:
            return IResource, GitHTTP(self.requestHandler, User(username)), lambda: None
        else:
            raise NotImplementedError()