from twisted.cred.credentials import IUsernamePassword, ISSHPrivateKey
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitexd.interfaces import IAuth
from gitexd.tests.plugins.default.default import UserStub, IUserStub

class Auth(object):
  implements(IPlugin, IAuth)

  SessionInterface = IUserStub

  def allowAnonymousAccess(self, app):
    return False

  def authenticateKey(self, app, credentials):
    assert ISSHPrivateKey.providedBy(credentials)

    return False

  def authenticatePassword(self, app, credentials):
    assert IUsernamePassword.providedBy(credentials)

    if credentials.username == "pass" and credentials.password == "test_pass":
      return defer.succeed(UserStub())
    else:
      return None

  def authorizeRepository(self, user, repository, requestType):
    return True

  def authorizeReferences(self, session, refs, requestType):
    return True

auth = Auth()