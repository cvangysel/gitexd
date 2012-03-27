import tempfile
from drupalgitdaemon.tests.plugins import authorization
from drupalgitdaemon.tests.test_authentication import AuthenticationTests
from gitdaemon.interfaces import IAuth
from gitdaemon.tests.test_daemonWorkflow import ApplicationTest
from gitdaemon.tests.test_repositoryEncapsulation import formatRemote

__author__ = 'christophe'

class AuthorizationTests(AuthenticationTests):

    pluginPackages = {
        IAuth: authorization
    }

    def testPasswordUserAuthorized(self):
        self._setUp()

        remoteRepository = self._testSSH("test", "passAuth")

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "pass").addCallback(processEnded)

    def testPasswordUserUnauthorized(self):
        self._setUp()

        remoteRepository = self._testSSH("john", "passAuth")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "pass").addCallback(processEnded)

    def testDefaultUserAuthorized(self):
        self._setUp()

        remoteRepository = self._testSSH("git", "keyAuth")

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, keyFile="test").addCallback(processEnded)

    def testDefaultUserUnauthorized(self):
        self._setUp()

        remoteRepository = self._testSSH("git", "keyAuth_invalid")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, keyFile="test").addCallback(processEnded)

    def testKeyUserAuthorized(self):
        self._setUp()

        remoteRepository = self._testSSH("test", "keyAuth")

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, keyFile="test").addCallback(processEnded)

    def testKeyUserUnauthorized(self):
        self._setUp()

        remoteRepository = self._testSSH("test", "keyAuth_invalid")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, keyFile="test").addCallback(processEnded)

    def testDisabledProject(self):
        self._setUp()

        remoteRepository = self._testSSH("test", "disabledProject")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "pass").addCallback(processEnded)

    def testDisabledUser(self):
        self._setUp()

        remoteRepository = self._testSSH("test", "disabledUsers")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "pass").addCallback(processEnded)