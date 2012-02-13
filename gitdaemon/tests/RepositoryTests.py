import random
import shutil
import tempfile
from twisted.internet.interfaces import ITransport
from twisted.trial import unittest

class GitTestHelper(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        from gitdaemon.git import Repository

        self.path = tempfile.mkdtemp()
        self.repository = Repository(self.path)

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

    def tearDown(self):
        shutil.rmtree(self.path)

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