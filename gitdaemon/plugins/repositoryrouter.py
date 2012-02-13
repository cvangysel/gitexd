import os
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon import Application
from gitdaemon.interfaces import IRepositoryRouter

class RepositoryRouter(object):
    implements(IPlugin, IRepositoryRouter)

    def route(self, app, repository):
        assert isinstance(app, Application)

        schemePath = app.getConfig().get("Repository", "repositoryBasePath")
        path = os.path.join(schemePath, *repository)

        if not os.path.exists(path):
            return None

        return path

repositoryRouter = RepositoryRouter()