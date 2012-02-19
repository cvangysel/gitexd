from ConfigParser import ConfigParser
from twisted.conch import avatar
from twisted.conch.interfaces import ISession
from twisted.conch.ssh import  userauth, connection, keys, session
from twisted.conch.ssh.factory import SSHFactory
from twisted.cred.portal import Portal
from twisted.internet.protocol import ProcessProtocol
from twisted.python import components
from zope.interface.declarations import implements
from gitdaemon import Object
from gitdaemon.error import UserException

class Session(object):
    implements(ISession)

    def __init__(self, user):
        assert isinstance(user, ConchUser)

        self.user = user

        self._invariant()

    def getPty(self, term, windowSize, attrs):
        self._invariant()

    def execCommand(self, proto, cmd):
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(cmd, str))
        self._invariant()

        self.user.app.getRequestHandler().handle(self.user.app, self.user.app.getRequestHandler().createSSHInvocationRequest(cmd, proto, self.user))

        assert proto.errConnectionLost() is None
        self._invariant()

    def openShell(self, proto):
        assert isinstance(proto, ProcessProtocol)
        self._invariant()

        self.user.app.getErrorHandler().handle(UserException("Hi!\nI can't open a shell for you at the moment. Sorry!\n\n", True, proto))

        self._invariant()

    def eofReceived(self):
        self._invariant()

    def closed(self):
        self._invariant()

    def _invariant(self):
        assert isinstance(self.user, ConchUser)

class ConchUser(avatar.ConchUser, Object):

    def __init__(self, app, username):
        avatar.ConchUser.__init__(self)
        Object.__init__(self, app)

        self.channelLookup.update({'session':session.SSHSession})

class Factory(SSHFactory):

    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

    def __init__(self, portal, config):
        assert isinstance(portal, Portal)
        assert isinstance(config, ConfigParser)

        self.portal = portal

        # TODO Place following logic in a try clause.
        self.privateKeys = {
            'ssh-rsa': keys.Key.fromFile(config.get("DEFAULT", "privateKeyLocation"))
        }

        self.publicKeys = {
            'ssh-rsa': keys.Key.fromFile(config.get("DEFAULT", "publicKeyLocation"))
        }

        if components.getAdapterFactory(ConchUser, ISession, None) == None:
            components.registerAdapter(Session, ConchUser, ISession)