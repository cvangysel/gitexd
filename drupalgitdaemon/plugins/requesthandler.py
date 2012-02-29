from twisted.plugin import IPlugin
from gitdaemon import Application
from gitdaemon.error import UserException, GitUserException
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler
from gitdaemon.plugins.requesthandler import InvocationRequestHandler

"""
    This file is a placeholder for when the basic logic
    for the InvocationRequestHandler is not compatible
    any more with the needs of Drupal.org.
"""

class DrupalInvocationRequestHandler(InvocationRequestHandler):
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    def handle(self, app, request):
        assert isinstance(app, Application)
        assert IInvocationRequest.providedBy(request)

        repository = app.getRepositoryRouter().route(app, request.getRepositoryPath())

        if repository is not None:
            if app.getAuth().mayAccess(request.getUser(), repository, False):
                request.invocate(repository)
            else:
                app.getErrorHandler().handle(GitUserException("You don't have access to this repository.", True, request.getProtocol()))
        else:
            app.getErrorHandler().handle(GitUserException("The specified repository doesn't exist.", True, request.getProtocol()))

#invocationRequestHandler = DrupalInvocationRequestHandler()