import random
import shutil
import tempfile

__author__ = 'christophe'

import unittest

class GitTestHelper(unittest.TestCase):

    def setUp(self):
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

    def createRandomFile(self):
        file = tempfile.NamedTemporaryFile(dir = self.path, delete = False)
        file.write(self.generateRandomString())
        file.close()

        return file.name

    def generateComplicatedCommit(self):
        assert self.repository.isValidGitRepository()

        self.repository.addFile(self.createRandomFile())
        self.repository.addFile(self.createRandomFile())

        self.repository.commit()

        self.repository.createBranch("second-branch")
        self.repository.switchBranch("second-branch")

        self.repository.addFile(self.createRandomFile())

        self.repository.commit()

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