import os
from gitexd.protocol.error import GitError

class UnexistingRepositoryException(GitError):
  def __init__(self, proto):
    GitError.__init__(self, "The specified repository doesn't exist.", proto)


def formatPackline(line):
  return "{0:04x}{1}".format(len(line) + 4, line)


def _findExecutable(executable):
  path = os.environ.get("PATH", os.defpath)

  fullPath = None

  for dir in path.split(":"):
    fullPath = os.path.join(dir, executable)

    if (os.path.exists(fullPath)) and (os.access(fullPath, (os.F_OK | os.X_OK))):
      break
    else:
      fullPath = None

  assert fullPath is not None and isinstance(fullPath, str)

  return fullPath


def getGit():
  return _findExecutable("git")

