from twisted.conch.ssh.keys import Key
from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from drupalgitdaemon import IUser, AnonymousUser, User
from drupalgitdaemon.service import IServiceProtocol, Service
from drupalgitdaemon.service.protocols import HTTPServiceProtocol
from gitdaemon import Application
from gitdaemon.interfaces import IAuth

class DrupalAuth(object):
    implements(IPlugin, IAuth)

    UserInterface = IUser

    def __init__(self):
        self.protocol = HTTPServiceProtocol

    def _handleProtocolCallback(self, result, app, data):
        assert isinstance(app, Application)
        assert isinstance(data, dict)

        if result:
            service = Service(self.protocol(app.getConfig(), 'vcs-auth-data'))

            return User(service, data)
        else:
            return None

    def allowAnonymousAccess(self, app):
        assert isinstance(app, Application)

        if app.getConfig().get("DEFAULT", "allowAnonymous", True):
            service = Service(self.protocol(app.getConfig(), 'vcs-auth-data'))

            return defer.succeed(AnonymousUser(service))
        else:
            return defer.succeed(None)

    def authenticateKey(self, app, credentials):
        assert isinstance(app, Application)
        assert ISSHPrivateKey.providedBy(credentials)

        key = Key.fromString(credentials.blob)
        fingerprint = key.fingerprint().replace(':', '')

        service = None
        data = {}

        if credentials.username == "git":
            service = Service(self.protocol(app.getConfig(), 'drupalorg-sshkey-check'))

            data = {
                "fingerprint": fingerprint
            }

            service.request_bool(data)
        else:
            service = Service(self.protocol(app.getConfig(), 'drupalorg-ssh-user-key'))

            data = {
                "username": credentials.username,
                "fingerprint": fingerprint
            }

            service.request_bool(data)

        service.addCallback(self._handleProtocolCallback, app, data)

        return service.deferred

    def authenticatePassword(self, app, credentials):
        assert isinstance(app, Application)
        assert IUsernamePassword.providedBy(credentials)

        service = Service(self.protocol(app.getConfig(), 'drupalorg-vcs-auth-check-user-pass'))

        data = {
            "username": credentials.username,
            "password": credentials.password
        }

        service.request_bool(data)

        service.addCallback(self._handleProtocolCallback, app, data)

        return service.deferred

    def mayAccess(self, app, user, repository, readOnly):
        assert isinstance(app, Application)
        assert isinstance(user, User)
        assert isinstance(readOnly, bool)

        """Whether or not the user may access the repository"""

        return user.mayAccess(repository, readOnly)

    def _invariant(self):
        assert IServiceProtocol.implementedBy(self._protocol)

auth = DrupalAuth()