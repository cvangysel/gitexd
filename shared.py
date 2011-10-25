from twisted.conch import avatar
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh import session
from twisted.cred import portal
from twisted.internet import protocol
from twisted.web.resource import IResource
from zope.interface.declarations import implements
from http import GitHTTP
from interface import IInvocationRequestHandler
import ssh

class GitRealm:
    implements(portal.IRealm)

    def __init__(self, requestHandler):
        self.requestHandler = requestHandler

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            print "SSH"
            return IConchUser, ssh.GitConchUser(avatarId, self.requestHandler), lambda: None
        elif IResource in interfaces:
            print "HTTP"
            return IResource, GitHTTP(self.requestHandler), lambda: None
        else:
            raise NotImplementedError()