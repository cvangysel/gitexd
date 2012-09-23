from ConfigParser import ConfigParser
import os
import random
import shutil
import tempfile
from twisted.internet import reactor, defer
from twisted.test.test_process import Accumulator
from twisted.trial import unittest
from gitexd import Factory
from gitexd.tests.git import Repository

class GitTestHelper(unittest.TestCase):
  def setUp(self):
    unittest.TestCase.setUp(self)

    self.path = self._generateRepositoryDirectory()
    self.repository = Repository(self.path)

    self.repoPath = tempfile.mkdtemp()

    self.success = None
    self.error = None
    self.permissionDenied = False

    self.output = None

  def _generateRepositoryDirectory(self, name=None, dir=None):
    if name is None:
      return tempfile.mkdtemp('', 'tmp', dir)
    else:
      if dir is not None:
        path = dir + "/" + name
      else:
        path = "/tmp/" + name

      os.mkdir(path)

      return path

  def generateRandomString(self, n=100):
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    string = ""

    for count in xrange(1, n):
      for x in random.sample(alphabet, random.randint(5, 15)):
        string += x

    return string

  def createRandomFile(self, path):
    file = tempfile.NamedTemporaryFile(dir=path, delete=False)
    file.write(self.generateRandomString())
    file.close()

    return file.name

  def generateComplicatedCommit(self, repository=None):
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

  def _executionCallback(self, output):
    self.output = output

    for o in output:
      if o.startswith("fatal: remote error: "):
        self.error = o[len("fatal: remote error: "):].rstrip("\n\r")
        self.success = False
      elif o.startswith("remote: error: "):
        self.error = o[len("remote: error: "):].split("\r\n")[0]
        self.success = False
      elif o.startswith("error: The requested URL returned error"):
        self.error = True
        self.success = False
      elif "fatal: The remote end hung up unexpectedly" in o or "fatal: Authentication failed" in o or "error:" in o:
        self.permissionDenied = True
        self.success = False
      elif "Writing objects: 100%" in o or "Unpacking objects: 100%" in o:
        self.success = True
      elif self.success is None:
        self.success = True

    return output

  def pushRepository(self, repository, password=None, keyFile=None):
    d = defer.Deferred()
    d.addCallback(self._executionCallback)

    p = GitProcess(d, password)
    reactor.spawnProcess(p, repository.git, [repository.git, "push", "--all", "origin"], path=repository.path,
                         usePTY=True, env=self._getEnvironmentVars(keyFile))

    return d

  def pullRepository(self, repository, password=None, keyFile=None):
    d = defer.Deferred()
    d.addCallback(self._executionCallback)

    p = GitProcess(d, password)
    reactor.spawnProcess(p, self.repository.git,
                         [self.repository.git, "pull", "origin", "master:master", "second-branch:second-branch"],
                         path=self.repository.path, usePTY=True, env=self._getEnvironmentVars(keyFile))

    return d

  def createTemporaryRepository(self, name=None, clone=None, bare=False, path=None):
    if path is None:
      path = self.repoPath

    path = self._generateRepositoryDirectory(name, dir=path)

    repository = Repository(path)

    if clone is not None:
      repository.clone(clone, bare)

    return repository

  def assertPermissionDenied(self):
    self.assertTrue(self.permissionDenied)
    self.assertFalse(self.success)

  def assertError(self, message=False):
    self.assertFalse(self.success)
    self.assertFalse(self.error is None)

    if isinstance(self.error, str):
      self.assertEqual(self.error, message, self.error)

  def assertNoError(self):
    self.assertTrue(self.success)
    self.assertTrue(self.error is None, self.error)

  def assertNotSuccess(self):
    self.assertFalse(self.success)

  def tearDown(self):
    shutil.rmtree(self.path)
    shutil.rmtree(self.repoPath)


class ApplicationTest(GitTestHelper):
  def setUp(self):
    GitTestHelper.setUp(self)

    self.config = _createDefaultConfigFile(self.repoPath)

    self.ssh = None
    self.http = None

  def startApplication(self, pluginPackages):
    self.app = Factory(self.config, pluginPackages)

    self.ssh = reactor.listenTCP(0, self.app.createSSHFactory())
    self.http = reactor.listenTCP(0, self.app.createHTTPFactory())

  def tearDown(self):
    if self.ssh:
      self.ssh.stopListening()

    if self.http:
      self.http.stopListening()

    GitTestHelper.tearDown(self)


class GitProcess(Accumulator):
  def __init__(self, d, password):
    assert isinstance(d, defer.Deferred)

    self.endedDeferred = d
    self.password = password
    self.output = []

  def outReceived(self, d):
    assert isinstance(d, str)

    if "Are you sure you want to continue connecting (yes/no)?" in d:
      self.transport.write("yes\n")

    if "password" in d.lower():
      if self.password is not None:
        self.transport.write(self.password + "\n")
      else:
        self.transport.write("\n")

    if "username" in d.lower():
      self.transport.write("\n")

    Accumulator.outReceived(self, d)

    self.output.append(d)

  def errReceived(self, d):
    Accumulator.errReceived(self, d)

  def processEnded(self, reason):
    self.closed = 1
    if self.endedDeferred is not None:
      d, self.endedDeferred = self.endedDeferred, None
      d.callback(self.output)

      self.output = []


def formatRemote(protocol, transport, repository, username=None, password=None):
  if username is None:
    auth = ""
  else:
    auth = username

    if password is not None:
      auth += ":" + password

    auth += "@"

  return protocol + "://" + auth + transport.getHost().host + ":" + str(transport.getHost().port) + "/" + repository


def _createDefaultConfigFile(repoPath='', defaults={}):
  keyPath = os.path.dirname(__file__) + "/example-key"

  config = ConfigParser(dict({
                               "privateKeyLocation": keyPath + "/key",
                               "publicKeyLocation": keyPath + "/key.pub",
                               'repositoryPath': repoPath
                             }.items() + defaults.items()))

  return config


class AuthenticationTest(ApplicationTest):
  def _testPush(self, user, HTTP=False):
    self.repository.initialize()

    remoteRepository = self.createTemporaryRepository(None, self.repository.path, True)

    if HTTP:
      self.repository.addRemote("origin", formatRemote("http", self.http, remoteRepository.path.split('/')[-1], user))
    else:
      self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteRepository.path.split('/')[-1], user))

    self.generateComplicatedCommit()

    return remoteRepository

  def _testPull(self, user, HTTP=False):
    self.repository.initialize()

    tempRepository = self.createTemporaryRepository(None, self.repository.path, False)
    self.generateComplicatedCommit(tempRepository)

    remoteRepository = self.createTemporaryRepository(None, tempRepository.path, True)
    remoteName = remoteRepository.path.split('/')[-1]

    if HTTP:
      self.repository.addRemote("origin", formatRemote("http", self.http, remoteName, user))
    else:
      self.repository.addRemote("origin", formatRemote("ssh", self.ssh, remoteName, user))

    return remoteRepository