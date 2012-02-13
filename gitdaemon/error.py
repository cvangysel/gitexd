from twisted.conch.ssh import session
from twisted.internet import protocol
from twisted.internet.interfaces import ITransport
from twisted.internet.protocol import ProcessProtocol
from zope.interface.declarations import implements
from gitdaemon.interfaces import IException

CRITICAL, NOTICE = range(0, 2)

class UserException(object):
    implements(IException)

    def __init__(self, message, critical = False, proto = None):
        assert isinstance(message, str)
        assert isinstance(critical, bool)
        assert proto is None or isinstance(proto, ProcessProtocol)

        self._message = message
        self._priority = CRITICAL if critical else NOTICE
        self._proto = proto

    def throw(self):
        self._logMessage()

        if isinstance(self._proto, ProcessProtocol):
            self._informUser()

    def _logMessage(self):
        """Logs the exception to the Twisted logger"""

        print self._message

    def _informUser(self):
        """Informs the user of the error and closes the connection if appropiate"""

        assert isinstance(self._proto, ProcessProtocol)

        protocol = ErrorProtocol(self._message, self._priority == CRITICAL)
        protocol.makeConnection(self._proto)
        self._proto.makeConnection(session.wrapProtocol(protocol))

    def getPriority(self):
        return self._priority

    def getMessage(self):
        return self._message

class GitUserException(UserException):

    def _informUser(self):
        assert isinstance(self._proto, ProcessProtocol)

        message = "{0:04x}{1}".format(len(self._message) + 4, self._message)

        protocol = ErrorProtocol(message, self._priority == CRITICAL)
        protocol.makeConnection(self._proto)
        self._proto.makeConnection(session.wrapProtocol(protocol))

class ErrorProtocol (protocol.Protocol):

    def __init__(self, message, loseConnection = False):
        assert isinstance(message, str) and len(message) > 0

        self._message = message
        self._loseConnection = loseConnection

    def connectionMade(self):
        if ITransport.providedBy(self.transport):

            self.transport.write(self._message)

            if (self._loseConnection):
                self.transport.loseConnection()