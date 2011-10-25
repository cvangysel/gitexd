#!/usr/bin/env python
from twisted.application.service import Application
from twisted.cred import checkers
from twisted.cred.credentials import DigestCredentialFactory
from twisted.cred.portal import Portal
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site


from twisted.python import components, log

from twisted.internet import reactor
import sys
from BaseImplementation import BaseInvocationRequestHandler
from shared import GitRealm

from ssh import *
from http import *

if __name__ == '__main__':
    print "Initializing"

    # log.startLogging(sys.stderr)

    requestHandler = BaseInvocationRequestHandler()

    application = Application("GitDaemon") # Create the application

    portal = Portal(GitRealm(requestHandler))

    passwdDB = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    passwdDB.addUser('user', 'password')

    portal.registerChecker(passwdDB)

    sshService = GitSSH(portal)
    # TODO might want to use DigestCredentialFactory here
    httpService = Site(HTTPAuthSessionWrapper(portal, [BasicCredentialFactory("GitDaemon")]))

    # sshService.setServiceParent(application)
    # httpService.setServiceParent(application);

    reactor.listenTCP(2222, sshService)
    reactor.listenTCP(8080, httpService)

    reactor.run()