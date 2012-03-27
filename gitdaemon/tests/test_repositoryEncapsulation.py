import os
import random
import shutil
import tempfile
from twisted.internet import defer, reactor
from twisted.internet.interfaces import ITransport
from twisted.test.test_process import Accumulator
from twisted.trial import unittest
from gitdaemon.git import Repository

def formatRemote(protocol, transport, repository, username = None, password = None):
    if username is None:
        auth = ""
    else:
        auth = username

        if password is not None:
            auth += ":" + password

        auth += "@"

    return protocol + "://" + auth + transport.getHost().host + ":" + str(transport.getHost().port) + "/" + repository

class GitTestHelper(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        from gitdaemon.git import Repository

        self.path = self._generateRepositoryDirectory()
        self.repository = Repository(self.path)

        self.repoPath = tempfile.mkdtemp()

    def _generateRepositoryDirectory(self, name = None, dir = None):
        if name is None:
            return tempfile.mkdtemp('', 'tmp', dir)
        else:
            print name, dir
            if dir is not None:
                path = dir + "/" + name
            else:
                path = "/tmp/" + name

            os.mkdir(path)

            return path

    def generateRandomString(self, n = 100):
        alphabet = "abcdefghijklmnopqrstuvwxyz"

        string= ""

        for count in xrange(1, n):
            for x in random.sample(alphabet,random.randint(5, 15)):
                string += x

        return string

    def createRandomFile(self, path):
        file = tempfile.NamedTemporaryFile(dir = path, delete = False)
        file.write(self.generateRandomString())
        file.close()

        return file.name

    def generateComplicatedCommit(self, repository = None):
        if repository is None:
            repository = self.repository

        assert repository.isValidGitRepository()

        repository.addFile(self.createRandomFile(repository.path))
        repository.addFile(self.createRandomFile(repository.path))

        repository.commit()

        repository.createBranch("second-branch")
        repository.switchBranch("second-branch")

        repository.addFile(self.createRandomFile(repository.path))

        repository.commit()

    def _getEnvironmentVars(self, keyFile):
        if keyFile is not None:
            sshWrapper = os.path.dirname(__file__) + "/example-key/sshWrapper.sh"

            return {
                "GIT_SSH": sshWrapper,
                "GIT_SSH_KEY": keyFile
            }

        return {}

    def pushRepository(self, repository, password = None, keyFile = None):
        p = GitProcess(password)
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, repository.pathToGit, [repository.pathToGit, "push", "--all", "origin"], path=repository.path, usePTY=True, env=self._getEnvironmentVars(keyFile))

        return d

    def pullRepository(self, repository, password = None, keyFile = None):
        p = GitProcess(password)
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, self.repository.pathToGit, [self.repository.pathToGit, "pull", "origin", "master:master", "second-branch:second-branch"], path=self.repository.path, usePTY=True, env=self._getEnvironmentVars(keyFile))

        return d

    def createTemporaryRepository(self, name = None, clone = None, bare = False, path = None):
        if path is None:
            path = self.repoPath

        path = self._generateRepositoryDirectory(name, dir=path)

        repository = Repository(path)

        if clone is not None:
            repository.clone(self.repository.path, bare)

        return repository

    def tearDown(self):
        shutil.rmtree(self.path)
        shutil.rmtree(self.repoPath)

class RepositoryTestCase(GitTestHelper):

    def testInvalidRepository(self):
        self.assertFalse(self.repository.isValidGitRepository())

    def testInitializeRepository(self):
        self.repository.initialize()

        self.assertTrue(self.repository.isValidGitRepository())

    def testAddRemoteRepository(self):
        self.repository.initialize()
        self.repository.addRemote("testSSH", "ssh://example.com/test.git")
        self.repository.addRemote("testHTTP", "http://example.com/test.git")

        output = self.repository.executeCommand("remote", ["-v"])

        self.assertTrue(output.find("ssh://example.com/test.git"))
        self.assertTrue(output.find("http://example.com/test.git"))

    def testAdvancedCommit(self):
        self.repository.initialize()
        self.generateComplicatedCommit()

        output = self.repository.executeCommand("status")

        self.assertTrue("master" not in output)
        self.assertTrue("nothing to commit" in output)

    def testCloneRepository(self):
        self.repository.initialize()
        self.generateComplicatedCommit()

        from gitdaemon.git import Repository
        path = tempfile.mkdtemp()
        clonedRepository = Repository(path)

        clonedRepository.clone(self.path)

        shutil.rmtree(path)

    def testEqual(self):
        self.repository.initialize()
        self.generateComplicatedCommit()

        from gitdaemon.git import Repository
        path = tempfile.mkdtemp()
        clonedRepository = Repository(path)

        clonedRepository.clone(self.path)

        self.assertEqual(self.repository, clonedRepository)

        shutil.rmtree(path)


class GitProcess(Accumulator):

    def __init__(self, password):
        self.password = password

    def outReceived(self, d):
        if "Are you sure you want to continue connecting (yes/no)?" in d:
            self.transport.write("yes\n")

        if "assword:" in d:
            if self.password is not None:
                self.transport.write(self.password + "\n")
            else:
                self.transport.write("\n")

        if "Username:" in d:
            self.transport.write("\n")

        Accumulator.outReceived(self, d)

    def errReceived(self, d):
        Accumulator.errReceived(self, d)

    def processEnded(self, reason):
        Accumulator.processEnded(self, reason)