from zope.interface.declarations import implements
from zope.interface.interface import Interface, Attribute

def getProjectName(repository):
    parts = repository.split('/')

    for part in parts:
        if len(part) > 4 and part[-4:] == '.git':
            return part[:-4]

    return None

class IUser(Interface):

    """ """

    service = Attribute("Service used to fetch information about repositories")

    def mayAccess(self, repository, readOnly = False, label = None):
        """ """

class User(object):
    implements(IUser)

    def __init__(self, service, data):
        assert isinstance(data, dict)

        self.service = service
        self.__dict__ = data

    def mayAccess(self, repository, readOnly = False, label = None):
        project = getProjectName(repository)

        print "mayAccess", repository, project

        if project is None:
            return False

        print "mayAccess", project

        self.service.request_json({
            "project_uri": project
        })

        def _authCallback(authService):
            assert isinstance(authService, dict)

            print authService

            return True

        self.service.deferred.addCallback(_authCallback)

        print "mayAccess"

        return self.service.deferred

class AnonymousUser(object):
    implements(IUser)

    def __init__(self, service):
        self.service = service

    def mayAccess(self, repository, readOnly = False, label = None):
        return True