from twisted.conch.error import ValidPublicKey
from twisted.conch.ssh.keys import Key
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword, IAnonymous
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.internet.protocol import ProcessProtocol
from twisted.python import log
from twisted.python.failure import Failure

from zope.interface import implements
import gitdaemon

class CredentialsChecker(gitdaemon.Object):

    def __init__(self, app):
        gitdaemon.Object.__init__(self, app)

    def errorHandler(self, fail, proto):
        self._invariant()
        assert isinstance(fail, Failure)
        assert isinstance(proto, ProcessProtocol)

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

        def authenticationCallback(result):
            if result:
                return credentials.username
            else:
                return Failure(UnauthorizedLogin(credentials.username))

        d = defer.maybeDeferred(self.verifySignature, credentials)
        d.addCallback(self.app.getAuth().authenticateKey, credentials)
        d.addCallback(authenticationCallback)
        d.addErrback(self.errorHandler)

        assert isinstance(d, defer.Deferred)

        return d

class PasswordChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IUsernamePassword,

    def requestAvatarId(self, credentials):
        self._invariant()
        assert IUsernamePassword.providedBy(credentials)

        def authenticationCallback(result):
            if result:
                return credentials.username
            else:
                return Failure(UnauthorizedLogin(credentials.username))

        d = defer.maybeDeferred(self.app.getAuth().authenticatePassword, credentials.username, credentials.password)
        d.addCallback(authenticationCallback)
        d.addErrback(self.errorHandler)

        assert isinstance(d, defer.Deferred)

        return d

class AnonymousChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IAnonymous,

    def requestAvatarId(self, credentials):
        self._invariant()
        assert IAnonymous.providedBy(credentials)

        def authenticationCallback(result):
            if result:
                return "anonymous"
            else:
                return Failure(UnauthorizedLogin("anonymous"))

        d = defer.maybeDeferred(self.app.getAuth().allowAnonymousAccess)
        d.addCallback(authenticationCallback)
        #d.addErrback(self.errorHandler)

        assert isinstance(d, defer.Deferred)

        return d
