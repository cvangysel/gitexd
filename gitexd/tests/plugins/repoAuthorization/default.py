from twisted.cred.credentials import IUsernamePassword, ISSHPrivateKey
from twisted.internet import defer
from twisted.plugin import IPlugin
from twisted.python.failure import Failure
from zope.interface.declarations import implements
from gitexd.interfaces import IAuth
from gitexd.protocol import PUSH, PULL
from gitexd.protocol.error import GitError
from gitexd.tests.plugins.default.default import UserStub, IUserStub

class Auth(object):
  implements(IPlugin, IAuth)

  SessionInterface = IUserStub

  def allowAnonymousAccess(self, app):
    return defer.succeed(UserStub())

  def authenticateKey(self, app, credentials):
    assert ISSHPrivateKey.providedBy(credentials)

    return defer.succeed(UserStub())

  def authenticatePassword(self, app, credentials):
    assert IUsernamePassword.providedBy(credentials)

    return False

  def authorizeRepository(self, user, repository, requestType):
    if requestType != PUSH:
      return Failure(GitError("Only PUSH requests are supported."))
    else:
      return True

  def authorizeReferences(self, session, refs, requestType):
    return True

auth = Auth()