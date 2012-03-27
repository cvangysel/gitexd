from twisted.python.failure import Failure
from zope.interface.declarations import implements
from zope.interface.interface import Interface, Attribute
from gitdaemon.error import GitUserException

def getProjectName(repository):
    parts = repository.split('/')

    for part in parts:
        if len(part) > 4 and part[-4:] == '.git':
            return part[:-4]

    return None

def _mapUser(users, username, password, fingerprint):
    assert isinstance(users, dict)
    assert username is None or isinstance(username, str)
    assert fingerprint is None or isinstance(fingerprint, str)

    if username is None and fingerprint is not None:
        for user in users.values():
            if fingerprint in user["ssh_keys"].values():
                return user
    elif username is not None and username in users:
        user = users[username]

        if fingerprint in user["ssh_keys"].values():
            return user
        elif password == user["pass"]:
            return user
        else:
            return None
    else:
        return None

class ISession(Interface):

    """ """

    service = Attribute("Service used to fetch information about repositories")

    def mayAccess(self, app, repository, readOnly = False, label = None):
        """ """

class Session(object):
    implements(ISession)

    def __init__(self, service, data):
        assert isinstance(data, dict)

        self._username = data["username"] if data.has_key("username") else None
        self._password = data["password"] if data.has_key("password") else None
        self._fingerprint = data["fingerprint"] if data.has_key("fingerprint") else None
        self._service = service

    def mayAccess(self, app, repository, readOnly = False, label = None):

        def _authCallback(data):
            assert isinstance(data, dict)

            if not readOnly:

                if not data["status"]:
                    return Failure(GitUserException("Project {0} has been disabled".format(data['repository_name'], True)))

                user = _mapUser(data["users"], self._username, self._password, self._fingerprint)

                if user is None:
                    return Failure(GitUserException("User '{1}' does not have write permissions for repository {0}".format(data['repository_name'], self._username)))
                elif not user["global"]:
                    return True
                else:
                    # Account is globally disabled or disallowed
                    # 0x01 = no Git user role, but unknown reason (probably a bug!)
                    # 0x02 = Git account suspended
                    # 0x04 = Git ToS unchecked
                    # 0x08 = Drupal.org account blocked
                    error = []

                    if user["global"] & 0x02:
                        error.append("Your Git access has been suspended.")
                    if user["global"] & 0x04:
                        error.append("You are required to accept the Git Access Agreement in your user profile before using Git.")
                    if user["global"] & 0x08:
                        error.append("Your Drupal.org account has been blocked.")

                    if len(error) == 0:
                        if user["global"] == 0x01:
                            error.append("You do not have permission to access '{0}' with the provided credentials.\n".format(data['repository_name']))
                        else:
                            error.append("This operation cannot be completed at this time.  It may be that we are experiencing technical difficulties or are currently undergoing maintenance.")

                    return Failure(GitUserException("\n".join(error)))
            else:
                # All repositories are publicly readable.
                return True

        project = getProjectName(repository)

        if project is None:
            return False

        self._service.request_json({
            "project_uri": project
        })

        self._service.deferred.addCallback(_authCallback)

        return self._service.deferred

class AnonymousSession(object):
    implements(ISession)

    def __init__(self, service):
        self.service = service

    def mayAccess(self, app, repository, readOnly = False, label = None):
        return readOnly