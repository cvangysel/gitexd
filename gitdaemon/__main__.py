from twisted.application.service import Application
from twisted.cred.portal import Portal
from twisted.plugin import getPlugins
from twisted.python import log
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.internet import reactor
from twisted.web.server import Site
from gitdaemon.protocol.authentication import PublicKeyChecker, PasswordChecker
from gitdaemon.protocol.ssh import GitSSH
from gitdaemon.shared.realm import Realm
import interfaces

if __name__ == '__main__':
    log.msg("Initializing GitDaemon ...")

    requestHandler = None
    for plugin in getPlugins(interfaces.IInvocationRequestHandler):
        requestHandler = plugin

    if requestHandler == None:
        log.err("Couldn't find a invocation plugin to handle requests")
    else:
        application = Application("GitDaemon") # Create the application

        portal = Portal(Realm(requestHandler))

        portal.registerChecker(PublicKeyChecker(requestHandler.Authentication))
        portal.registerChecker(PasswordChecker(requestHandler.Authentication))

        sshService = GitSSH(portal)
        # TODO might want to use DigestCredentialFactory here
        httpService = Site(HTTPAuthSessionWrapper(portal, [BasicCredentialFactory("GitDaemon")]))

        # sshService.setServiceParent(application)
        # httpService.setServiceParent(application);

        reactor.listenTCP(2222, sshService)
        reactor.listenTCP(8080, httpService)

        reactor.run()