import os
import subprocess
from twisted.internet import utils

def _findExecuteable(executable):
    path = os.environ.get("PATH", os.defpath)

    fullPath = None

    for dir in path.split(":"):
        fullPath = os.path.join(dir, executable)

        if (os.path.exists(fullPath)) and (os.access(fullPath, (os.F_OK | os.X_OK))):
            break
        else:
            fullPath = None

    assert fullPath != None and isinstance(fullPath, str)

    return fullPath

def findGitShell():
    return _findExecuteable("git-shell")

def findGitHTTPBackend():
    return "/usr/lib/git-core/git-http-backend"


class Repository(object):

    pathToGit = _findExecuteable("git")

    def __init__(self, path):
        assert isinstance(path, str)
        assert os.path.exists(path)

        self.path = path
        self.bare = False
        
        self._invariant()

    def getGitCommand(self, command, arg = []):
        """Generates the command-line command including arguments to be executed in the repository."""

        assert isinstance(command, str)
        assert len(command) > 0
        assert isinstance(arg, list)
        self._invariant()

        ret = [command] + arg

        assert isinstance(ret, list)
        assert len(ret) == len(arg) + 1
        self._invariant()

        return ret

    def executeCommand(self, command, arg = []):
        """Executes a Git command with certain arguments in the repository and returns the output.
                Command execution is done outside of Twisted.

                This command is mainly a convenience method for tests."""

        assert isinstance(command, str)
        assert len(command) > 0
        assert isinstance(arg, list)
        self._invariant()

        arguments = self.getGitCommand(command, arg)

        print [self.pathToGit] + arguments

        output = subprocess.check_output([self.pathToGit] + arguments, stderr=subprocess.STDOUT, cwd=self.path)

        print output

        assert isinstance(output, str)
        self._invariant()

        return output

    def initialize(self):
        self._invariant()
        assert not self.isValidGitRepository()

        self.executeCommand("init")

        self._invariant()
        assert self.isValidGitRepository()

    def clone(self, url, bare=False):
        self._invariant()
        assert not self.isValidGitRepository()
        assert isinstance(url, str)
        assert isinstance(bare, bool)

        arg = [url, "."]

        if bare:
            arg.append("--bare")
            self.bare = True

        self.executeCommand("clone", arg)

        self._invariant()
        assert self.isValidGitRepository()

    def push(self, remote = "origin", branch = ""):
        assert isinstance(remote, str) and len(remote) > 0
        assert isinstance(branch, str)
        self._invariant()
        assert self.isValidGitRepository()

        if len(branch) > 0:
            arg = [remote, branch]
        else:
            arg = [remote]

        print self.executeCommand("push", arg)

        self._invariant()
        assert self.isValidGitRepository()

    def pull(self, remote = "origin", branch = "master"):
        assert isinstance(remote, str) and len(remote) > 0
        assert isinstance(branch, str) and len(branch) > 0
        assert self.isValidGitRepository()
        self._invariant()

        self.executeCommand("pull", [remote, branch])

        self._invariant()
        assert self.isValidGitRepository()

    def addRemote(self, name, remote):
        assert isinstance(remote, str) and len(remote) > 0
        assert isinstance(name, str) and len(name) > 0
        assert remote.startswith("ssh://") or remote.startswith("http://")
        assert self.isValidGitRepository()
        self._invariant()

        output = self.executeCommand("remote", ["add", name, remote])

        self._invariant()
        assert len(output) == 0
        assert self.isValidGitRepository()

    def addFile(self, filename):
        assert isinstance(filename, str) and len(filename) > 0
        assert self.isValidGitRepository()
        self._invariant()

        output = self.executeCommand("add", [filename])

        self._invariant()
        assert len(output) == 0
        assert self.isValidGitRepository()

    def commit(self, message = "No commit message specified"):
        assert isinstance(message, str) and len(message) > 0
        assert self.isValidGitRepository()
        self._invariant()

        output = self.executeCommand("commit", ["-m", message])

        self._invariant()
        assert message in output
        assert self.isValidGitRepository()

    def createBranch(self, name):
        assert isinstance(name, str) and len(name) > 0
        assert self.isValidGitRepository()
        self._invariant()

        output = self.executeCommand("branch", [name])

        self._invariant()
        assert isinstance(output, str) and len(output) == 0
        assert self.isValidGitRepository()

    def switchBranch(self, name):
        assert isinstance(name, str) and len(name) > 0
        assert self.isValidGitRepository()
        self._invariant()

        output = self.executeCommand("checkout", [name])

        self._invariant()
        assert name in output
        assert self.isValidGitRepository()

    def isValidGitRepository(self):
        self._invariant

        if self.bare:
            return os.path.exists(self.path + "/HEAD")
        else:
            return os.path.exists(self.path + "/.git")

    def _invariant(self):
        assert isinstance(self.path, str)
        assert os.path.exists(self.pathToGit)
        assert isinstance(self.bare, bool)

    def __eq__(self, other):
        assert self.isValidGitRepository()

        assert isinstance(other, Repository)
        assert other.isValidGitRepository()

        try:
            selfLog = self.executeCommand("log", ["HEAD", "--pretty=oneline", "--all"]).split("\n")
        except subprocess.CalledProcessError:
            selfLog = ""

        try:
            otherLog = other.executeCommand("log", ["HEAD", "--pretty=oneline", "--all"]).split("\n")
        except subprocess.CalledProcessError:
            otherLog = ""

        return set(selfLog) == set(otherLog)

    def __ne__(self, other):
        return not self.__eq__(other)