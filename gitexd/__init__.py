class Object(object):

    def __init__(self, app):
        assert isinstance(app, Factory)

        self.app = app

        self._invariant()

    def _invariant(self):
        assert isinstance(self.app, Factory)

from types import ModuleType
from gitexd.protocol.authentication import Realm
from ConfigParser import ConfigParser
from twisted.cred.portal import Portal
from twisted.plugin import getPlugins
from zope.interface import Interface
from gitexd.protocol import ssh, http
import interfaces
import plugins

class Factory(object):

    def __init__(self, config, pluginPackages = {}):
        assert isinstance(config, ConfigParser)
        assert isinstance(pluginPackages, dict)

        self._config = config
        self._pluginPackages = pluginPackages

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

        return ssh.Factory(self._portal, self._config)

    def createHTTPFactory(self):
        self._invariant()

        return http.Factory(self._portal, self._config)

    def _loadPlugins(self):

        def loadPlugin(pluginInterface, pluginPackages = {}):
            assert issubclass(pluginInterface, Interface)
            assert isinstance(pluginPackages, dict)

            plugin = None

            if pluginPackages.has_key(pluginInterface) and isinstance(pluginPackages[pluginInterface], ModuleType):
                pluginPackage = pluginPackages[pluginInterface]
            else:
                pluginPackage = plugins

            pluginList = getPlugins(pluginInterface, pluginPackage)

            for plugin in pluginList:
                break

            assert plugin is not None
            assert pluginInterface.providedBy(plugin)

            return plugin

        self._requestHandler = loadPlugin(interfaces.IRequestHandler, self._pluginPackages)
        self._auth = loadPlugin(interfaces.IAuth, self._pluginPackages)
        self._errorHandler = loadPlugin(interfaces.IExceptionHandler, self._pluginPackages)
        self._repositoryRouter = loadPlugin(interfaces.IRepositoryRouter, self._pluginPackages)

        assert interfaces.IRequestHandler.providedBy(self._requestHandler)
        assert interfaces.IAuth.providedBy(self._auth)
        assert interfaces.IExceptionHandler.providedBy(self._errorHandler)
        assert interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)

    def _invariant(self):
        assert isinstance(self._pluginPackages, dict)
        assert isinstance(self._config, ConfigParser)
        assert isinstance(self._portal, Portal)
        assert interfaces.IRequestHandler.providedBy(self._requestHandler)
        assert interfaces.IAuth.providedBy(self._auth)
        assert interfaces.IExceptionHandler.providedBy(self._errorHandler)
        assert interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)