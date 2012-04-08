from twisted.internet.interfaces import IProcessProtocol
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.protocol.error import ErrorProtocol
from gitdaemon.interfaces import IExceptionHandler, IException

class ExceptionHandler(object):
    implements(IPlugin, IExceptionHandler)

    def handle(self, exception, protocol = None):
        assert IException.providedBy(exception)
        assert IProcessProtocol.providedBy(protocol) or protocol is None

        if protocol is None:
            protocol = exception.getProtocol()

        errorProtocol = ErrorProtocol(str(exception))
        errorProtocol.makeConnection(protocol)

exceptionHandler = ExceptionHandler()