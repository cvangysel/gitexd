from twisted.internet import reactor
from twisted.trial import unittest
from gitdaemon import Application
from gitdaemon.tests import plugins
from gitdaemon.tests.test_subsystemPlugins import _createDefaultConfigFile
from gitdaemon.tests.test_repositoryEncapsulation import GitTestHelper, formatRemote
from gitdaemon.interfaces import IAuth

__author__ = 'christophe'

class ApplicationTest(GitTestHelper):

    def setUp(self):
        GitTestHelper.setUp(self)

        self.config = _createDefaultConfigFile(self.repoPath)

        self.ssh = None
        self.http = None

    def startApplication(self, pluginPackages):
        self.app = Application(self.config, pluginPackages)

        self.ssh = reactor.listenTCP(0, self.app.createSSHFactory())
        self.http = reactor.listenTCP(0, self.app.createHTTPFactory())

    def tearDown(self):
        if self.ssh:
            self.ssh.stopListening()

        if self.http:
            self.http.stopListening()

        GitTestHelper.tearDown(self)

class ApplicationGitTests(ApplicationTest):

    def setUp(self):
        ApplicationTest.setUp(self)

        self.startApplication(pluginPackages = {
            IAuth: plugins.default
        })

    def testSSHPush(self):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1]))
        self.generateComplicatedCommit()

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository, "derp").addCallback(processEnded)

    def testHTTPPush(self):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("http", self.http, remoteRepository.path.split('/')[-1]))
        self.generateComplicatedCommit()

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

    def testSSHPull(self):
        self.repository.initialize()

        otherRepository = self.createTemporaryRepository(self.repository.path, False)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, otherRepository.path.split('/')[-1]))
        self.generateComplicatedCommit(otherRepository)

        def processEnded(result):
            self.assertEqual(self.repository, otherRepository)

        self.assertNotEqual(self.repository, otherRepository)

        return self.pullRepository(self.repository).addCallback(processEnded)

    def testHTTPPull(self):
        self.repository.initialize()

        otherRepository = self.createTemporaryRepository(self.repository.path, False)

        self.repository.addRemote("origin", formatRemote("http", self.http, otherRepository.path.split('/')[-1]) + "/.git")
        self.generateComplicatedCommit(otherRepository)

        def processEnded(result):
            self.assertEqual(self.repository, otherRepository)

        self.assertNotEqual(self.repository, otherRepository)

        return self.pullRepository(self.repository).addCallback(processEnded)

if __name__ == '__main__':
    unittest.main()
