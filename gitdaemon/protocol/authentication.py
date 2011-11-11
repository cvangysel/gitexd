from twisted.conch.error import ValidPublicKey
from twisted.conch.ssh.keys import Key
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import ISSHPrivateKey, IUsernamePassword
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.python import log
from twisted.python.failure import Failure
from zope.interface import implements

class CredentialsChecker:
     def __init__(self, authentication):
        self.authentication = authentication

class PublicKeyChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = ISSHPrivateKey,

    def verifySignature(self, credentials):
        key = Key.fromString(credentials.blob)

        if not credentials.signature:
            return Failure(ValidPublicKey())
        else:
            try:
                if key.verify(credentials.signature, credentials.sigData):
                    return key
            except:
                log.err()

                return Failure(UnauthorizedLogin("Key could not be verified"))

    def requestAvatarId(self, credentials):
        def authenticationCallback(result):
            if result:
                return credentials.username
            else:
                return Failure(UnauthorizedLogin(credentials.username))

        d = defer.maybeDeferred(self.verifySignature, credentials)
        d.addCallback(self.authentication.authenticateKey, credentials)
        d.addCallback(authenticationCallback)

        return d

class PasswordChecker(CredentialsChecker):
    implements(ICredentialsChecker)

    credentialInterfaces = IUsernamePassword,

    def requestAvatarId(self, credentials):
        def authenticationCallback(result):
            if result:
                return credentials.username
            else:
                return Failure(UnauthorizedLogin(credentials.username))

        d = defer.maybeDeferred(self.authentication.authenticatePassword, credentials.username, credentials.password)
        d.addCallback(authenticationCallback)

        return d