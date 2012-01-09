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

        try:
            output = subprocess.check_output([self.pathToGit] + arguments, stderr=subprocess.STDOUT, cwd=self.path)
        except subprocess.CalledProcessError:
            return False

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

    def push(self, remote = "origin", branch = "origin"):
        assert isintance(remote, str) and len(remote) > 0
        assert isinstance(branch, str) and len(branch) > 0
        self._invariant()
        assert self.isValidGitRepository()

        print self.executeCommand("push", [remote, branch])

        self._invariant()
        assert self.isValidGitRepository()

    def pull(self, remote = "origin", branch = "origin"):
        assert isintance(remote, str) and len(remote) > 0
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

        return os.path.exists(self.path + "/.git")

    def _invariant(self):
        assert isinstance(self.path, str)
        assert os.path.exists(self.pathToGit)