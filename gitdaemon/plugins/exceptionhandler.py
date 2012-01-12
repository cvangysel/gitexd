from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IExceptionHandler

class ErrorHandler(object):
    implements(IPlugin, IExceptionHandler)

    def invoke(self, e):
        """Handles a user-invoked exception"""

errorHandler = ErrorHandler()