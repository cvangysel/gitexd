from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.python import log
from zope.interface.declarations import implements
from gitdaemon.interfaces import IExceptionHandler, IException

class ExceptionHandler(object):
    implements(IPlugin, IExceptionHandler)

    def handle(self, exception, proto = None):
        assert IException.providedBy(exception)
        assert proto is None or isinstance(proto, ProcessProtocol)

        if proto is not None:
            exception.bindProtocol(proto)

        exception.throw()

exceptionHandler = ExceptionHandler()