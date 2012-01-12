from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IExceptionHandler, IException

class ExceptionHandler(object):
    implements(IPlugin, IExceptionHandler)

    def handle(self, exception):
        assert IException.providedBy(exception)

        print exception.getMessage()
        exception.throw()

exceptionHandler = ExceptionHandler()