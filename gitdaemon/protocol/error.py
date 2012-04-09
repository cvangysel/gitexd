from twisted.internet import protocol
from twisted.internet.interfaces import ITransport, IProcessProtocol
from zope.interface.declarations import implements
from gitdaemon.interfaces import IException

class Error(Exception):
    implements(IException)

    def __init__(self, message, proto = None):
        Exception.__init__(self)

        assert isinstance(message, str)
        assert proto is None or IProcessProtocol.providedBy(self._proto)

        self._message = message
        self._proto = proto

    def __str__(self):
        return self._formatMessage()

    def _formatMessage(self):
        return self._message

    def getMessage(self):
        return self._message

    def getProtocol(self):
        return self._proto

class GitError(Error):

    def __init__(self, message, proto = None):
        Error.__init__(self, message, proto)

    def _formatMessage(self):
        from git import formatPackline

        message = formatPackline("ERR " + self._message)
        return message

class ErrorProtocol(protocol.Protocol):

    def __init__(self, message):
        assert isinstance(message, str) and len(message) > 0

        self._message = message

    def connectionMade(self):
        if ITransport.providedBy(self.transport):
            self.transport.write(self._message)

            if self.transport is not None:
                self.transport.loseConnection()