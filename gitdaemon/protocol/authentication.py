from defer import Deferred
from exceptions import NotImplementedError
from twisted.conch.error import ValidPublicKey
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh.keys import Key
from twisted.cred import portal
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword, IAnonymous, ICredentials
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.internet.protocol import ProcessProtocol
from twisted.python import log
from twisted.python.failure import Failure
from twisted.web.resource import IResource

import gitdaemon

from zope.interface import implements
from gitdaemon.protocol.http import Script
from gitdaemon.protocol.ssh import ConchUser


class CredentialsChecker(gitdaemon.Object):

    def __init__(self, app):
        gitdaemon.Object.__init__(self, app)

    def authenticationCallback(result, credentials):
        assert ICredentials.providedBy(credentials)

        if result != False or result != None:
            return result
        else:
            return Failure(UnauthorizedLogin(credentials))

    def authenticationCallback(self, d, credentials):
        assert d is Deferred
        assert ICredentials.providedBy(credentials)

        d.addCallback(authenticationCallback, credentials)
        d.addErrback(self.errorHandler, None)

        assert isinstance(d, defer.Deferred)

        return d

    def errorHandler(self, fail, proto):
        self._invariant()
        assert isinstance(fail, Failure)
        #assert isinstance(proto, ProcessProtocol)

        fail.trap(Failure)

        message = fail.value

        if proto.connectionMade():
            proto.loseConnection()

        # TODO This should be passed to ErrorHandler
        #self.authentication.errorHandler(message, proto)

        assert not proto.connectionMade()

class PublicKeyChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = ISSHPrivateKey,

    def verifySignature(self, credentials):
        self._invariant()
        assert ISSHPrivateKey.providedBy(credentials)

        key = Key.fromString(credentials.blob)

        if not credentials.signature:
            ret = Failure(ValidPublicKey())
        else:
            try:
                if key.verify(credentials.signature, credentials.sigData):
                    ret = key
            except:
                log.err()

                ret = Failure(UnauthorizedLogin("Key could not be verified"))

        assert isinstance(ret, Failure) or ret == key

    def requestAvatarId(self, credentials):
        self._invariant()
        assert ISSHPrivateKey.providedBy(credentials)

        d = defer.maybeDeferred(self.verifySignature, credentials)
        d.addCallback(self.app.getAuth().authenticateKey, credentials)

        return d

class PasswordChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IUsernamePassword,

    def requestAvatarId(self, credentials):
        self._invariant()
        assert IUsernamePassword.providedBy(credentials)

        d = defer.maybeDeferred(self.app.getAuth().authenticatePassword, credentials.username, credentials.password)

        assert isinstance(d, defer.Deferred)

        return d

class AnonymousChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IAnonymous,

    def requestAvatarId(self, credentials):
        self._invariant()
        assert IAnonymous.providedBy(credentials)

        d = defer.maybeDeferred(self.app.getAuth().allowAnonymousAccess)

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