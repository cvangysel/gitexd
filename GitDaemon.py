#!/usr/bin/env python
from twisted.application.service import Application
from twisted.cred.credentials import DigestCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site


from twisted.python import components, log

from twisted.internet import reactor
import sys

from ssh import *
from http import *

if __name__ == '__main__':
    print "Initializing"

    # log.startLogging(sys.stderr)

    application = Application("GitDaemon") # Create the application
    
    portal = Portal(GitRealm())
    passwdDB = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    passwdDB.addUser('user', 'password')

    portal.registerChecker(passwdDB)

    components.registerAdapter(GitSession, GitConchUser, ISession)

    sshService = GitSSH(portal)
    httpService = Site(HTTPAuthSessionWrapper(portal, [DigestCredentialFactory("md5", "localhost:8080")]))

    # sshService.setServiceParent(application)
    # httpService.setServiceParent(application);

    reactor.listenTCP(2222, sshService)
    reactor.listenTCP(8080, httpService)

    reactor.run()