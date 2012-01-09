import os
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitdaemon.interfaces import IRepositoryRouter

class RepositoryRouter(object):
    implements(IPlugin, IRepositoryRouter)

    def route(self, repository):
        schemePath = '/home/christophe/Desktop/repositories' #config.get("GitDaemon", "repositoryBasePath")
        path = os.path.join(schemePath, *repository)

        if not os.path.exists(path):
            print "Repo " + path + " does not exist on disk"

            return None
            # Do protocol independent error stuff

        return path

repositoryRouter = RepositoryRouter()