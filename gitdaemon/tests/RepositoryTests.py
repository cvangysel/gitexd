import shutil
import tempfile
from gitdaemon.git import Repository

__author__ = 'christophe'

import unittest

class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.repository = Repository(self.path)

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

    def tearDown(self):
        shutil.rmtree(self.path)