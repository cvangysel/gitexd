from twisted.conch import avatar
from twisted.conch.interfaces import ISession
from twisted.conch.ssh import  userauth, connection, keys, session
from twisted.conch.ssh.factory import SSHFactory
from twisted.internet.protocol import ProcessProtocol
from twisted.python import components
from zope.interface.declarations import implements
from gitdaemon import Object
from gitdaemon.error import UserException

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

        if components.getAdapterFactory(ConchUser, ISession, None) == None:
            components.registerAdapter(Session, ConchUser, ISession)