from twisted.internet import protocol
from twisted.internet.interfaces import ITransport, IProcessProtocol
from zope.interface.declarations import implements
from gitexd.interfaces import IException

class Error(Exception):
  implements(IException)

  def __init__(self, message, proto=None):
    Exception.__init__(self)

    assert isinstance(message, str)
    assert proto is None or IProcessProtocol.providedBy(proto)

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
  def __init__(self, message, proto=None):
    Error.__init__(self, message, proto)

  def _formatMessage(self):
    return self._message


class ErrorProtocol(protocol.Protocol):
  def __init__(self, message):
    assert isinstance(message, str) and len(message) > 0

    self._message = message

  def connectionMade(self):
    from gitexd.protocol import GitProcessProtocol

    if isinstance(self.transport, GitProcessProtocol):
      self.transport.die(self._message)