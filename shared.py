from twisted.conch import avatar
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh import session
from twisted.cred import portal
from twisted.web.resource import IResource
from zope.interface.declarations import implements
from http import GitHTTP
import ssh

class GitRealm:
    implements(portal.IRealm)

    def __init__(self):
        """Todo"""

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            print "SSH"
            return interfaces[0], ssh.GitAvatar(avatarId), lambda: None
        elif IResource in interfaces:
            print "HTTP"
            return IResource, GitHTTP(), lambda: None
        else:
            raise NotImplementedError()