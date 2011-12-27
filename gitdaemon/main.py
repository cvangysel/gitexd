from twisted.cred.portal import Portal
from twisted.plugin import getPlugins
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site
from zope.interface import Interface
import interfaces
import plugins
from protocol.authentication import PublicKeyChecker, PasswordChecker
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

    _portal = None

    _requestHandler = None
    _authenticationH = None
    _errorHandler = None
    _repositoryRouter = None

    def __init__(self):
        self._loadPlugins()

        self._requestHandler.attachRouter(self._repositoryRouter)

        self._portal = Portal(Realm(self._requestHandler))

        self._portal.registerChecker(PublicKeyChecker(self._authentication))
        self._portal.registerChecker(PasswordChecker(self._authentication))

        assert self._invariant()

    def createSSHFactory(self):
        assert self._invariant()

        return GitSSH(self._portal)

    def createHTTPFactory(self):
        assert self._invariant()

        # TODO might want to use DigestCredentialFactory here
        return Site(HTTPAuthSessionWrapper(self._portal, [BasicCredentialFactory("GitDaemon")]))

    def _loadPlugins(self):
        self._requestHandler = loadPlugin(interfaces.IInvocationRequestHandler)
        self._authentication = loadPlugin(interfaces.IAuthentication)
        self._errorHandler = loadPlugin(interfaces.IErrorHandler)
        self._repositoryRouter = loadPlugin(interfaces.IRepositoryRouter)

        assert interfaces.IInvocationRequestHandler.providedBy(self._requestHandler)
        assert interfaces.IAuthentication.providedBy(self._authentication)
        assert interfaces.IErrorHandler.providedBy(self._errorHandler)
        assert interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)

    def _invariant(self):
        return  isinstance(self._portal, Portal) and\
                interfaces.IInvocationRequestHandler.providedBy(self._requestHandler) and\
                interfaces.IAuthentication.providedBy(self._authentication) and\
                interfaces.IErrorHandler.providedBy(self._errorHandler) and\
                interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)
