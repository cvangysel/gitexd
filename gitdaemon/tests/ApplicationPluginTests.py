from ConfigParser import ConfigParser
from twisted.internet import reactor
import time
from gitdaemon import Application, interfaces

__author__ = 'christophe'

import unittest

class ApplicationPluginTests(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser({'repositoryBasePath': ''})

    def testBasicPlugins(self):
        app = Application(self.config)

        self.assertTrue(interfaces.IAuth.providedBy(app.getAuth()))
        self.assertTrue(interfaces.IInvocationRequestHandler.providedBy(app.getRequestHandler()))
        self.assertTrue(interfaces.IErrorHandler.providedBy(app.getErrorHandler()))
        self.assertTrue(interfaces.IRepositoryRouter.providedBy(app.getRepositoryRouter()))

    def testBasicExecution(self):
        app = Application(self.config)

        def testCase(test, app):
            time.sleep(.1)
            reactor.stop()

            test.assertTrue(app._invariant)

        reactor.listenTCP(2020, app.createSSHFactory())
        reactor.listenTCP(8888, app.createHTTPFactory())

        reactor.callInThread(testCase, self, app)
        reactor.run()

if __name__ == '__main__':
    unittest.main()
