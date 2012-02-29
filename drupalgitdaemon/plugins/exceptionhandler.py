from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IExceptionHandler, IException

"""
    This file is a placeholder for when the basic logic
    for the ExceptionHandler is not compatible any more
    with the needs of Drupal.org.
"""

class DrupalExceptionHandler(object):
    implements(IPlugin, IExceptionHandler)

    def handle(self, exception):
        assert IException.providedBy(exception)

        exception.throw()

#exceptionHandler = DrupalExceptionHandler()