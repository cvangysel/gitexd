
from ConfigParser import ConfigParser
import shutil
from subprocess import CalledProcessError
import tempfile
from twisted.internet import reactor
from gitdaemon import Application
from gitdaemon.tests.RepositoryTests import GitTestHelper

__author__ = 'christophe'

import unittest

class ApplicationGitTests(GitTestHelper):

    def setUp(self):
        GitTestHelper.setUp(self)

        self.repoPath = tempfile.mkdtemp()
        self.config = ConfigParser({'repositoryBasePath': self.repoPath})

        self.app = Application(self.config)

        self.sshPort = 2455;
        self.httpPort = 4578;

    def runTest(self, testCase):
        reactor.listenTCP(self.sshPort, self.app.createSSHFactory())
        reactor.listenTCP(self.httpPort, self.app.createHTTPFactory())

        reactor.callInThread(testCase, self, self.app)
        reactor.run()

    def testSSHPush(self):
        def testCase(test, app):
            self.repository.initialize()
            self.repository.addRemote("origin", "ssh://127.0.0.1:" + str(self.sshPort))

            test.generateComplicatedCommit()

            try:
                self.repository.push()
            except CalledProcessError as e:
                print e.output

            reactor.stop()

        self.runTest(testCase)

    def tearDown(self):
        reactor.crash()

        GitTestHelper.tearDown(self)

if __name__ == '__main__':
    unittest.main()
