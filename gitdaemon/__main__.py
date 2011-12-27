import sys
from twisted.internet import reactor
from twisted.python import log
from main import Application

if __name__ == "__main__":
    log.startLogging(sys.stderr)

    git = Application()

    ssh = git.createSSHFactory()
    http = git.createHTTPFactory()

    reactor.listenTCP(2222, ssh)
    reactor.listenTCP(8080, http)

    reactor.run()