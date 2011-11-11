import os
from twisted.internet import reactor
import sys

def findGitComponent(component):
    component = "git-" + component

    path = os.environ.get("PATH", os.defpath)

    for dir in path.split(":"):
        fullPath = os.path.join(dir, component)
        if (os.path.exists(fullPath)) and (os.access(fullPath, (os.F_OK | os.X_OK))):
            return fullPath
    raise Exception("Couldn't find " + component)

def findGitShell():
    return findGitComponent("shell")

def findGitError():
    return findGitComponent("error")

def findGitHTTPBackend():
    return "/usr/lib/git-core/git-http-backend"