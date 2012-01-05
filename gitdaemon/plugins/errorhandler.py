from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IErrorHandler

class ErrorHandler(object):
    implements(IPlugin, IErrorHandler)

    def invoke(self, e):
        """Handles a user-invoked exception"""

errorHandler = ErrorHandler()