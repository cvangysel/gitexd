from gitexd.interfaces import IAuth
from gitexd.tests import ApplicationTest, formatRemote
from gitexd.tests.plugins import error

class ErrorTests(ApplicationTest):
  def setUp(self):
    ApplicationTest.setUp(self)

    self.startApplication(pluginPackages={
      IAuth: error
    })

  def testSSHError(self):
    self.repository.initialize()

    remoteRepository = self.createTemporaryRepository(None, self.repository.path, True)

    self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1]))
    self.generateComplicatedCommit()

    def processEnded(result):
      self.assertError("Hello world")
      self.assertNotEqual(self.repository, remoteRepository)

    return self.pushRepository(self.repository, "derp", keyFile = "test").addCallback(processEnded)

  def testHTTPError(self):
    self.repository.initialize()

    remoteRepository = self.createTemporaryRepository(None, self.repository.path, True)

    self.repository.addRemote("origin", formatRemote("http", self.http, remoteRepository.path.split('/')[-1]))
    self.generateComplicatedCommit()

    def processEnded(result):
      self.assertError("Hello world")
      self.assertNotEqual(self.repository, remoteRepository)

    return self.pushRepository(self.repository).addCallback(processEnded)