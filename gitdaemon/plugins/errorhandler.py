from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IErrorHandler

class ErrorHandler(object):
    implements(IPlugin, IErrorHandler)

errorHandler = ErrorHandler()