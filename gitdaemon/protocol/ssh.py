from twisted.conch import avatar
from twisted.conch.avatar import ConchUser
from twisted.conch.interfaces import ISession
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.conch.ssh.factory import SSHFactory
from twisted.internet import protocol
from twisted.internet.interfaces import ITransport
from twisted.internet.protocol import ProcessProtocol
from twisted.python import components
from zope.interface.declarations import implements, providedBy
import zope
from gitdaemon.interfaces import IInvocationRequestHandler
from gitdaemon.shared.user import User

publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""

class ShellProtocol (protocol.Protocol):

    def connectionMade(self):
        assert ITransport.providedBy(self.transport)

        self.transport.write("Hi! I only accept SSH sessions through Git.\r\nSorry.\r\n")
        self.transport.loseConnection()

class GitConchSession(object):
    implements(ISession)

    def __init__(self, user):
        self.user = user

        assert self.invariant()

    def getPty(self, term, windowSize, attrs):
        pass

    def execCommand(self, proto, cmd):
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(cmd, str))

        assert self.invariant()

        self.user.requestHandler.handle(self.user.requestHandler.createSSHInvocationRequest(cmd, proto, self.user))

        assert proto.errConnectionLost() == 11

        assert self.invariant()

    def openShell(self, proto):
        assert isinstance(proto, ProcessProtocol)

        assert self.invariant()

        protocol = ShellProtocol()
        protocol.makeConnection(proto)
        proto.makeConnection(session.wrapProtocol(protocol))

        assert proto.errConnectionLost() == 11

        assert self.invariant()

    def eofReceived(self):
        pass

    def closed(self):
        pass

    def invariant(self):
        return IInvocationRequestHandler.providedBy(self.user.requestHandler)

class GitConchUser(ConchUser, User):

    def __init__(self, username, requestHandler):
        avatar.ConchUser.__init__(self)
        User.__init__(self, username)

        self.channelLookup.update({'session':session.SSHSession})
        self.requestHandler = requestHandler

class GitSSH(SSHFactory):

    publicKeys = {
        'ssh-rsa': keys.Key.fromString(data=publicKey)
    }
    privateKeys = {
        'ssh-rsa': keys.Key.fromString(data=privateKey)
    }
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

    def __init__(self, portal):
        self.portal = portal
        
        components.registerAdapter(GitConchSession, GitConchUser, ISession)