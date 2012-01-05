from twisted.cred.portal import Portal
from twisted.plugin import getPlugins
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site
from zope.interface import Interface
import interfaces
import plugins
from protocol.authentication import PublicKeyChecker, PasswordChecker, AnonymousChecker
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

    __instance = None

    _portal = None

    _requestHandler = None
    _authentication = None
    _authorization = None
    _errorHandler = None
    _repositoryRouter = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            print "NEW APP OBJ"
            cls.__instance = super(Application, cls).__new__(cls, *args, **kwargs)
            cls.__instance._initialize()
        else:
            print "OLD APP OBJ"

        return cls.__instance

    def _initialize(self):
        assert not self._invariant()

        print "APPLICATION OBJECT CONSTRUCTOR"
        self._loadPlugins()

        self._portal = Portal(Realm(self._requestHandler))

        self._portal.registerChecker(PublicKeyChecker(self._authentication))
        self._portal.registerChecker(PasswordChecker(self._authentication))
        self._portal.registerChecker(AnonymousChecker(self._authentication))

        assert self._invariant()

    def requestHandler(self):
        assert self._invariant()

        return self._requestHandler

    def authentication(self):
        assert self._invariant()

        return self._authentication

    def authorization(self):
        assert self._invariant()

        return self._authorization

    def errorHandler(self):
        assert self._invariant()

        return self._errorHandler

    def repositoryRouter(self):
        assert self._invariant()

        return self._repositoryRouter

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
        self._authorization = loadPlugin(interfaces.IAuthorization)
        self._errorHandler = loadPlugin(interfaces.IErrorHandler)
        self._repositoryRouter = loadPlugin(interfaces.IRepositoryRouter)

        print "AUTHENTICATION: ", self._authentication
        print "AUTHORIZATION: ", self._authorization

        assert interfaces.IInvocationRequestHandler.providedBy(self._requestHandler)
        assert interfaces.IAuthentication.providedBy(self._authentication)
        assert interfaces.IAuthorization.providedBy(self._authorization)
        assert interfaces.IErrorHandler.providedBy(self._errorHandler)
        assert interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)

    def _invariant(self):
        return  isinstance(self._portal, Portal) and\
                interfaces.IInvocationRequestHandler.providedBy(self._requestHandler) and\
                interfaces.IAuthentication.providedBy(self._authentication) and\
                interfaces.IAuthorization.providedBy(self._authorization) and\
                interfaces.IErrorHandler.providedBy(self._errorHandler) and\
                interfaces.IRepositoryRouter.providedBy(self._repositoryRouter)
