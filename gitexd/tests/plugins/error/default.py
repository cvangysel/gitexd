from twisted.internet import defer
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
from zope.interface.declarations import implements
from gitexd.protocol.error import GitError
from gitexd.interfaces import IAuth
from gitexd.tests.plugins.default.default import UserStub, IUserStub

class Auth(object):
    implements(IPlugin, IAuth)

    SessionInterface = IUserStub

    def allowAnonymousAccess(self, app):
        return defer.succeed(UserStub())

    def authenticateKey(self, app, credentials):
        return defer.succeed(UserStub())

    def authenticatePassword(self, app, credentials):
        return defer.succeed(UserStub())

    def authorizeRepository(self, user, repository, readOnly):
        return Failure(GitError("Hello world"))

    def authorizeReferences(self, session, refs, requestType):
        return True

auth = Auth()