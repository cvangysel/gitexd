from exceptions import NotImplementedError
from twisted.conch.error import ValidPublicKey
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh.keys import Key
from twisted.cred import portal
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword, IAnonymous, ICredentials
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer, reactor
from twisted.python import log
from twisted.python.failure import Failure
from twisted.web.resource import IResource

import gitdaemon

from zope.interface import implements
from gitdaemon.protocol.http import Script
from gitdaemon.protocol.ssh import ConchUser

def authenticationErrorHandler(fail):
    # TODO Possibly combine with authorizationErrorHandler
    assert isinstance(fail, Failure)

    r = fail.trap(UnauthorizedLogin, ValidPublicKey, NotImplementedError, Exception)

    if r == UnauthorizedLogin:
        fail.trap(Failure)
    elif r == ValidPublicKey:
        """Ignore."""
    elif r == NotImplementedError:
        """NotImplemented, sometimes used for testing."""

        fail.printTraceback()
        reactor.stop()
    else:
        """Unknown exception, halt excecution."""

        fail.printTraceback()
        reactor.stop()

class CredentialsChecker(gitdaemon.Object):

    def __init__(self, app):
        gitdaemon.Object.__init__(self, app)

    def authCallback(self, result, credentials):
        assert ICredentials.providedBy(credentials)

        if result == False or result is None:
            return Failure(UnauthorizedLogin())
        else:
            return result

class PublicKeyChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = ISSHPrivateKey,

    def authCallback(self, result, credentials):

        """Adapted from twisted.conch.checkers.SSHPublicKeyDatabase._cbRequestAvatarId"""

        assert ICredentials.providedBy(credentials)

        if result == False or result is None:
            return Failure(UnauthorizedLogin())
        elif not credentials.signature:
            return Failure(ValidPublicKey())
        else:
            try:
                pubKey = Key.fromString(credentials.blob)

                if pubKey.verify(credentials.signature, credentials.sigData):
                    return result
            except:
                log.err()

            return Failure(UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        self._invariant()
        assert ISSHPrivateKey.providedBy(credentials)

        d = defer.maybeDeferred(self.app.getAuth().authenticateKey, self.app, credentials)
        d.addCallback(self.authCallback, credentials)

        d.addErrback(authenticationErrorHandler)

        assert isinstance(d, defer.Deferred)

        return d

class PasswordChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IUsernamePassword,

    def requestAvatarId(self, credentials):
        self._invariant()
        assert IUsernamePassword.providedBy(credentials)

        d = defer.maybeDeferred(self.app.getAuth().authenticatePassword, self.app, credentials)
        d.addCallback(self.authCallback, credentials)

        d.addErrback(authenticationErrorHandler)

        assert isinstance(d, defer.Deferred)

        return d

class AnonymousChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IAnonymous,

    def requestAvatarId(self, credentials):
        self._invariant()
        assert IAnonymous.providedBy(credentials)

        d = defer.maybeDeferred(self.app.getAuth().allowAnonymousAccess, self.app)
        d.addCallback(self.authCallback, credentials)

        d.addErrback(authenticationErrorHandler)

        assert isinstance(d, defer.Deferred)

        return d

class Realm(gitdaemon.Object):
    implements(portal.IRealm)

    def __init__(self, app):
        gitdaemon.Object.__init__(self, app)

    def requestAvatar(self, obj, mind, *interfaces):
        if IConchUser in interfaces:
            return IConchUser, ConchUser(self.app, obj), lambda: None
        elif IResource in interfaces:
            return IResource, Script(self.app, obj), lambda: None
        else:
            raise NotImplementedError()