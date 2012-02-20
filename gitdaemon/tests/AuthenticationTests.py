from gitdaemon.interfaces import IAuth
from gitdaemon.tests.ApplicationGitTests import ApplicationTest
from gitdaemon.tests.RepositoryTests import GitTestHelper, formatRemote
from gitdaemon.tests.plugins import keyAuth, passAuth

__author__ = 'christophe'

class KeyAuthenticationTests(ApplicationTest):

    def setUp(self):
        ApplicationTest.setUp(self)

        self.startApplication(pluginPackages = {
            IAuth: keyAuth
        })

    def _test(self, user):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1], user))
        self.generateComplicatedCommit()

        return remoteRepository

    def testAnonymous(self):
        remoteRepository = self._test(None)

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

    def testInvalidUser(self):
        remoteRepository = self._test("random")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

    def testValidUser(self):
        remoteRepository = self._test("key")

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

class PasswordAuthenticationTests(ApplicationTest):

    def setUp(self):
        ApplicationTest.setUp(self)

        self.startApplication(pluginPackages = {
            IAuth: passAuth
        })

    def _testSSH(self, user):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1], user))
        self.generateComplicatedCommit()

        return remoteRepository

    def _testHTTP(self, user):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("http", self.http, remoteRepository.path.split('/')[-1], user))
        self.generateComplicatedCommit()

        return remoteRepository

    def testSSHInvalidUser(self):
        remoteRepository = self._testSSH("random")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

    def testHTTPInvalidUser(self):
        remoteRepository = self._testHTTP("random")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

    def testSSHValidUserWrongPassword(self):
        remoteRepository = self._testSSH("pass")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "test").addCallback(processEnded)

    def testHTTPValidUserWrongPassword(self):
        remoteRepository = self._testHTTP("pass")

        def processEnded(result):
            self.assertNotEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "test").addCallback(processEnded)

    def testSSHValidUser(self):
        remoteRepository = self._testSSH("pass")

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "test_pass").addCallback(processEnded)

    def testHTTPValidUser(self):
        remoteRepository = self._testHTTP("pass")

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "test_pass").addCallback(processEnded)