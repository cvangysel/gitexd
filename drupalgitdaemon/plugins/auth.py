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

    def _handleProtocolCallback(self, result):
        if result:
            return User()
        else:
            return None

    def allowAnonymousAccess(self, app):
        assert isinstance(app, Application)

        if app.getConfig().get("DEFAULT", "allowAnonymous", True):
            return defer.succeed(AnonymousUser())
        else:
            return defer.succeed(None)

    def authenticateKey(self, app, credentials):
        assert isinstance(app, Application)
        assert ISSHPrivateKey.providedBy(credentials)

        key = Key.fromString(credentials.blob)
        fingerprint = key.fingerprint().replace(':', '')

        service = None

        if credentials.username == "git":
            service = Service(self.protocol(app.getConfig(), 'drupalorg-sshkey-check'))

            service.request_bool({
                "fingerprint": fingerprint
            })
        else:
            service = Service(self.protocol(app.getConfig(), 'drupalorg-ssh-user-key'))

            service.request_bool({
                "username": credentials.username,
                "fingerprint": fingerprint
            })

        service.addCallback(self._handleProtocolCallback)

        return service.deferred

    def authenticatePassword(self, app, credentials):
        assert isinstance(app, Application)
        assert IUsernamePassword.providedBy(credentials)

        service = Service(self.protocol(app.getConfig(), 'drupalorg-vcs-auth-check-user-pass'))

        service.request_bool({
            "username": credentials.username,
            "password": credentials.password
        })

        service.addCallback(self._handleProtocolCallback)

        return service.deferred

    def mayAccess(self, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return True

    def _invariant(self):
        assert IServiceProtocol.implementedBy(self._protocol)

auth = DrupalAuth()