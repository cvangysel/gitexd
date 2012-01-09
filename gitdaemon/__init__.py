from twisted.plugin import IPlugin, getPlugins
# hack to clear cache
list(getPlugins(IPlugin))

class Object(object):

    def __init__(self, app):
        assert isinstance(app, Application)

        self.app = app

        self._invariant()

    def _invariant(self):
        assert isinstance(self.app, Application)

from ConfigParser import ConfigParser
from twisted.cred.portal import Portal
from twisted.plugin import getPlugins
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site
from zope.interface import Interface
import interfaces
import plugins
from protocol.ssh import GitSSH
from shared.realm import Realm

def loadPlugin(pluginInterface, name = "base"):
    assert issubclass(pluginInterface, Interface)
    assert isinstance(name, str) and len(name) > 0

    plugin = None

    pluginList = getPlugins(pluginInterface, plugins)

    for plugin in pluginList:
        if name == name:
            break

    assert plugin != None, pluginInterface

    return plugin

class Application(object):

    def __init__(self, config):
        assert isinstance(config, ConfigParser)

        self._config = config;

        self._loadPlugins()

        self._portal = Portal(Realm(self))

        from protocol.authentication import PublicKeyChecker, PasswordChecker, AnonymousChecker
        self._portal.registerChecker(PublicKeyChecker(self))
        self._portal.registerChecker(PasswordChecker(self))
        self._portal.registerChecker(AnonymousChecker(self))

        self._invariant()

    def getRequestHandler(self):
        self._invariant()

        return self._requestHandler

    def getAuth(self):
        self._invariant()

        return self._auth

    def getErrorHandler(self):
        self._invariant()

        return self._errorHandler

    def getRepositoryRouter(self):
        self._invariant()

        return self._repositoryRouter

    def getConfig(self):
        self._invariant()

        return self._config

    def createSSHFactory(self):
        self._invariant()

        return GitSSH(self._portal)

    def createHTTPFactory(self):
        self._invariant()

        # TODO might want to use DigestCredentialFactory here
        return Site(HTTPAuthSessionWrapper(self._portal, [BasicCredentialFactory("GitDaemon")]))

    def _loadPlugins(self):
        self._requestHandler = loadPlugin(interfaces.IInvocationRequestHandler)
        self._auth = loadPlugin(interfaces.IAuth)
        self._errorHandler = loadPlugin(interfaces.IErrorHandler)
        self._repositoryRouter = loadPlugin(interfaces.IRepositoryRouter)

        assert interfaces.IInvocationRequestHandler.providedBy(self._requestHandler)
        assert interfaces.IAuth.providedBy(self._auth)
        assert interfaces.IErrorHandler.providedBy(self._errorHandler)
        assert interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)

    def _invariant(self):
        assert isinstance(self._config, ConfigParser)
        assert isinstance(self._portal, Portal)
        assert interfaces.IInvocationRequestHandler.providedBy(self._requestHandler)
        assert interfaces.IAuth.providedBy(self._auth)
        assert interfaces.IErrorHandler.providedBy(self._errorHandler)
        assert interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)