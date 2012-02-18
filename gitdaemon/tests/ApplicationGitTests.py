from ConfigParser import ConfigParser
import shutil
import tempfile
from twisted.internet import reactor, defer
from twisted.trial import unittest
from gitdaemon import Application
from gitdaemon.git import Repository
from gitdaemon.tests.ApplicationPluginTests import _createDefaultConfigFile
from gitdaemon.tests.RepositoryTests import GitTestHelper, GitProcess, formatRemote
from gitdaemon.tests import plugins
from gitdaemon.interfaces import IAuth

__author__ = 'christophe'

class ApplicationGitTests(GitTestHelper):

    def setUp(self):
        GitTestHelper.setUp(self)

        self.config = self.config = _createDefaultConfigFile(self.repoPath)

        pluginPackages = {
            IAuth: plugins
        }

        self.app = Application(self.config, pluginPackages)

        self.ssh = reactor.listenTCP(0, self.app.createSSHFactory())
        self.http = reactor.listenTCP(0, self.app.createHTTPFactory())

    def testSSHPush(self):
        self.repository.initialize()

        remoteRepository = self.createTemporaryRepository(self.repository.path, True)

        self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1]))
        self.generateComplicatedCommit()

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return self.pushRepository(self.repository).addCallback(processEnded)

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

    def tearDown(self):
        self.ssh.stopListening()
        self.http.stopListening()

        GitTestHelper.tearDown(self)

if __name__ == '__main__':
    unittest.main()
