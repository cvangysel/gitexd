import os
from twisted.internet import reactor
import sys

def findGitComponent(component):
    component = "git-" + component

    path = os.environ.get("PATH", os.defpath)

    fullPath = None

    for dir in path.split(":"):
        fullPath = os.path.join(dir, component)
        if (os.path.exists(fullPath)) and (os.access(fullPath, (os.F_OK | os.X_OK))):
            break
        else:
            fullPath = None

    assert fullPath != None and isinstance(fullPath, str)

    return fullPath

def findGitShell():
    return findGitComponent("shell")

def findGitHTTPBackend():
    return "/usr/lib/git-core/git-http-backend"
