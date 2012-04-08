from twisted.internet import reactor
from twisted.trial import unittest
from gitdaemon import Application, interfaces
from gitdaemon.interfaces import IInvocationRequestHandler
from gitdaemon.tests import plugins, _createDefaultConfigFile
from gitdaemon.tests.plugins.default.default import StubInvocationRequestHandler

class ApplicationPluginTests(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.config = _createDefaultConfigFile()

    def testBasicPlugins(self):
        app = Application(self.config)

        self.assertTrue(interfaces.IAuth.providedBy(app.getAuth()))
        self.assertTrue(interfaces.IInvocationRequestHandler.providedBy(app.getRequestHandler()))
        self.assertTrue(interfaces.IExceptionHandler.providedBy(app.getErrorHandler()))
        self.assertTrue(interfaces.IRepositoryRouter.providedBy(app.getRepositoryRouter()))

    def testBasicExecution(self):
        app = Application(self.config)

        ssh = reactor.listenTCP(0, app.createSSHFactory())
        http = reactor.listenTCP(0, app.createHTTPFactory())

        app._invariant()

        ssh.stopListening()
        http.stopListening()

    def testPluggedPlugins(self):
        pluginPackages = {
            IInvocationRequestHandler: plugins.default
        }

        app = Application(self.config, pluginPackages)

        ssh = reactor.listenTCP(0, app.createSSHFactory())
        http = reactor.listenTCP(0, app.createHTTPFactory())

        app._invariant()
        self.assertTrue(app.getRequestHandler(), StubInvocationRequestHandler)

        ssh.stopListening()
        http.stopListening()

if __name__ == '__main__':
    unittest.main()