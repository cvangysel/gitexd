from twisted.internet import defer
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
from zope.interface.declarations import implements
from gitdaemon.protocol.error import GitError
from gitdaemon.interfaces import IAuth
from gitdaemon.tests.plugins.default.default import UserStub, IUserStub

class Auth(object):
    implements(IPlugin, IAuth)

    UserInterface = IUserStub

    def allowAnonymousAccess(self, app):
        return defer.succeed(UserStub())

    def authenticateKey(self, app, credentials):
        return defer.succeed(UserStub())

    def authenticatePassword(self, app, credentials):
        return defer.succeed(UserStub())

    def authorizeRepository(self, app, user, repository, readOnly):
        """Whether or not the user may access the repository"""

        return Failure(GitError("Hello world"))

auth = Auth()