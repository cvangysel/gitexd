"""
    The Secure Shell transport protocol offers authentication through password and shared key mechanisms. The connection is also automatically
    encrypted for secure communications.

    Client requests are processed as commands that get executed through the protocol. It is not possible to open a shell or request a pseudo
    terminal for security reasons. The executed commands should be processed correctly in the plugin that implements the IRequestHandler interface.
"""

from ConfigParser import ConfigParser
from twisted.conch import avatar
from twisted.conch.avatar import ConchUser
from twisted.conch.interfaces import ISession
from twisted.conch.ssh import  userauth, connection, keys, session
from twisted.conch.ssh.factory import SSHFactory
from twisted.cred.portal import Portal
from twisted.internet.protocol import ProcessProtocol
from twisted.python import components
from zope.interface.declarations import implements
from zope.interface.interface import Interface
from gitexd import Object
from gitexd.protocol import GitProcessProtocol
from gitexd.protocol.error import Error

class GitProcessProtocol(GitProcessProtocol):

    def die(self, message):
        self._proto.session.write(message)

        if self._processTransport is not None:
            self._die()

class Session(object):
    implements(ISession)

    class SSHShellException(Error):

        def __init__(self, proto):
            Error.__init__(self, "Hi!\nI can't open a shell for you at the moment. Sorry!\n\n", proto)

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

        self.user.app.getRequestHandler().handle(self.user.app, self.user.app.getRequestHandler().createSSHRequest(self.user.app, cmd, proto, self.user.getAuthSession()))

        assert proto.errConnectionLost() is None
        self._invariant()

    def openShell(self, proto):
        assert isinstance(proto, ProcessProtocol)
        self._invariant()

        self.user.app.getErrorHandler().handle(SSHShellException(proto))

        self._invariant()

    def eofReceived(self):
        self._invariant()

    def closed(self):
        self._invariant()

    def _invariant(self):
        if self.user.app.getAuth().SessionInterface is Interface:
            assert self.user.app.getAuth().SessionInterface.providedBy(self.user.getAuthSession())

        assert isinstance(self.user, ConchUser)

class ConchUser(avatar.ConchUser, Object):

    def __init__(self, app, sess):
        avatar.ConchUser.__init__(self)
        Object.__init__(self, app)

        self.channelLookup.update({'session':session.SSHSession})

        self._session = sess

    def getAuthSession(self):
        return self._session

class Factory(SSHFactory):

    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

    def __init__(self, portal, config):
        assert isinstance(portal, Portal)
        assert isinstance(config, ConfigParser)

        self.portal = portal

        self.privateKeys = {
            'ssh-rsa': keys.Key.fromFile(config.get("DEFAULT", "privateKeyLocation"))
        }

        self.publicKeys = {
            'ssh-rsa': keys.Key.fromFile(config.get("DEFAULT", "publicKeyLocation"))
        }

        if components.getAdapterFactory(ConchUser, ISession, None) is None:
            components.registerAdapter(Session, ConchUser, ISession)