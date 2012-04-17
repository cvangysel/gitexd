from twisted.cred.credentials import IUsernamePassword, ISSHPrivateKey
from twisted.internet import defer
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
from zope.interface.declarations import implements
from gitdaemon.interfaces import IAuth
from gitdaemon.protocol import PUSH, PULL
from gitdaemon.protocol.error import GitError
from gitdaemon.tests.plugins.default.default import UserStub, IUserStub

class Auth(object):
    implements(IPlugin, IAuth)

    UserInterface = IUserStub

    def allowAnonymousAccess(self, app):
        return defer.succeed(UserStub())

    def authenticateKey(self, app, credentials):
        assert ISSHPrivateKey.providedBy(credentials)

        return defer.succeed(UserStub())

    def authenticatePassword(self, app, credentials):
        assert IUsernamePassword.providedBy(credentials)

        return False

    def authorizeRepository(self, user, repository, requestType):
        return True

    def authorizeReferences(self, session, refs, requestType):
        if requestType == PUSH:
            labels = map(lambda x: x[2].rstrip('\x00'), refs)
            branches = map(lambda x: x[11:], filter(lambda x: x.startswith("refs/heads/"), labels))

            if "second-branch" in branches:
                return Failure(GitError("You are not allowed to PUSH to second-branch."))
            else:
                return False
        elif requestType == PULL:
            return True
        else:
            return False

auth = Auth()