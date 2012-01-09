from ConfigParser import ConfigParser
import sys
from twisted.internet import reactor
from twisted.python import log
from gitdaemon import Application

if __name__ == "__main__":
    log.startLogging(sys.stderr)

    config = ConfigParser({'repositoryBasePath': '/home/christophe/Desktop/repositories'})

    git = Application(config)

    ssh = git.createSSHFactory()
    http = git.createHTTPFactory()

    reactor.listenTCP(2222, ssh)
    reactor.listenTCP(8080, http)

    reactor.run()