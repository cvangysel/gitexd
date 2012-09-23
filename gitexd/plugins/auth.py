from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword
from twisted.internet import defer
from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from gitexd.interfaces import IAuth

class Auth(object):
  implements(IPlugin, IAuth)

  """Trivial implementation of the auth plugin that doesn't check anything."""

  SessionInterface = None

  def allowAnonymousAccess(self, app):
    return defer.succeed(True)

  def authenticateKey(self, app, credentials):
    assert ISSHPrivateKey.providedBy(credentials)

    return defer.succeed(True)

  def authenticatePassword(self, app, credentials):
    assert IUsernamePassword.providedBy(credentials)

    return defer.succeed(True)

  def authorizeRepository(self, user, repository, readOnly):
    return True

  def authorizeReferences(self, session, refs, requestType):
    return True

auth = Auth()