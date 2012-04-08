from gitdaemon.interfaces import IAuth
from gitdaemon.tests import formatRemote
from gitdaemon.tests.plugins import default
from gitdaemon.tests.test_workflow import ApplicationTest

class PerLabelAuthorizationTests(ApplicationTest):

    def setUp(self):
        ApplicationTest.setUp(self)

        self.startApplication(pluginPackages = {
            IAuth: default
        })

    def testSSHPush(self):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(None, self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1]))
        self.generateComplicatedCommit()

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "derp").addCallback(processEnded)

    def testHTTPPush(self):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(None, self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("http", self.http, remoteRepository.path.split('/')[-1]))
        self.generateComplicatedCommit()

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

    def testSSHPull(self):
        self.repository.initialize()

        otherRepository = self.createTemporaryRepository(None, self.repository.path, False)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, otherRepository.path.split('/')[-1]))
        self.generateComplicatedCommit(otherRepository)

        def processEnded(result):
            self.assertEqual(self.repository, otherRepository)

        self.assertNotEqual(self.repository, otherRepository)

        return self.pullRepository(self.repository).addCallback(processEnded)

    def testHTTPPull(self):
        self.repository.initialize()

        otherRepository = self.createTemporaryRepository(None, self.repository.path, False)

        self.repository.addRemote("origin", formatRemote("http", self.http, otherRepository.path.split('/')[-1]) + "/.git")
        self.generateComplicatedCommit(otherRepository)

        def processEnded(result):
            self.assertEqual(self.repository, otherRepository)

        self.assertNotEqual(self.repository, otherRepository)

        return self.pullRepository(self.repository).addCallback(processEnded)