from ConfigParser import ConfigParser
import shutil
import tempfile
from twisted.internet import reactor, defer
from twisted.test.test_process import Accumulator
from twisted.trial import unittest
from gitdaemon import Application
from gitdaemon.git import Repository
from gitdaemon.tests.RepositoryTests import GitTestHelper
from gitdaemon.tests import plugins
from gitdaemon.interfaces import IAuth

__author__ = 'christophe'

class GitProcess(Accumulator):

    def outReceived(self, d):
        print "'" + d + "'"

        if "Are you sure you want to continue connecting (yes/no)?" in d:
            self.transport.write("yes\n")

        Accumulator.outReceived(self, d)

    def errReceived(self, d):
        print d
        Accumulator.errReceived(self, d)

    def processEnded(self, reason):
        print reason
        Accumulator.processEnded(self, reason)

class ApplicationGitTests(GitTestHelper):

    def setUp(self):
        GitTestHelper.setUp(self)

        self.repoPath = tempfile.mkdtemp()
        self.config = ConfigParser({'repositoryBasePath': self.repoPath})
        self.config.add_section("Repository")
        self.config.set("Repository", 'repositoryBasePath',  self.repoPath)

        pluginPackages = {
            IAuth: plugins
        }

        self.app = Application(self.config, pluginPackages)

        self.ssh = reactor.listenTCP(0, self.app.createSSHFactory())
        self.http = reactor.listenTCP(0, self.app.createHTTPFactory())

    def testSSHPush(self):
        remoteRepositoryPath = tempfile.mkdtemp(dir=self.repoPath)
        remoteRepository = Repository(remoteRepositoryPath)

        self.repository.initialize()

        remoteRepository.clone(self.repository.path, True)

        self.repository.addRemote("origin", "ssh://127.0.0.1:" + str(self.ssh.getHost().port) + "/" + remoteRepositoryPath.split('/')[-1])

        self.generateComplicatedCommit()

        p = GitProcess()
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, self.repository.pathToGit, [self.repository.pathToGit, "push", "--all", "origin"], path=self.repository.path, usePTY=True)

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return d.addCallback(processEnded)

    def testHTTPPush(self):
        remoteRepositoryPath = tempfile.mkdtemp(dir=self.repoPath)
        remoteRepository = Repository(remoteRepositoryPath)

        self.repository.initialize()

        remoteRepository.clone(self.repository.path, True)

        self.repository.addRemote("origin", "http://127.0.0.1:" + str(self.http.getHost().port) + "/" + remoteRepositoryPath.split('/')[-1])

        self.generateComplicatedCommit()

        p = GitProcess()
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, self.repository.pathToGit, [self.repository.pathToGit, "push", "--all", "origin"], path=self.repository.path, usePTY=True)

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return d.addCallback(processEnded)

    def testSSHPull(self):
        remoteRepositoryPath = tempfile.mkdtemp(dir=self.repoPath)
        remoteRepository = Repository(remoteRepositoryPath)

        self.repository.initialize()

        remoteRepository.clone(self.repository.path)
        self.generateComplicatedCommit(remoteRepository)

        self.assertNotEqual(self.repository, remoteRepository)

        self.repository.addRemote("origin", "ssh://127.0.0.1:" + str(self.ssh.getHost().port) + "/" + remoteRepositoryPath.split('/')[-1])

        p = GitProcess()
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, self.repository.pathToGit, [self.repository.pathToGit, "pull", "origin", "master:master", "second-branch:second-branch"], path=self.repository.path, usePTY=True)

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return d.addCallback(processEnded)

    def testHTTPPull(self):
        remoteRepositoryPath = tempfile.mkdtemp(dir=self.repoPath)
        remoteRepository = Repository(remoteRepositoryPath)

        self.repository.initialize()

        remoteRepository.clone(self.repository.path)
        self.generateComplicatedCommit(remoteRepository)

        self.assertNotEqual(self.repository, remoteRepository)

        self.repository.addRemote("origin", "http://127.0.0.1:" + str(self.http.getHost().port) + "/" + remoteRepositoryPath.split('/')[-1] + "/.git")

        p = GitProcess()
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, self.repository.pathToGit, [self.repository.pathToGit, "pull", "origin", "master:master", "second-branch:second-branch"], path=self.repository.path, usePTY=True)

        def processEnded(result):
            self.assertEqual(self.repository, remoteRepository)

        return d.addCallback(processEnded)

    def tearDown(self):
        self.ssh.stopListening()
        self.http.stopListening()

        shutil.rmtree(self.repoPath)

        GitTestHelper.tearDown(self)

if __name__ == '__main__':
    unittest.main()
