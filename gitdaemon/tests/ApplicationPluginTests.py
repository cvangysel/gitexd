from ConfigParser import ConfigParser
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

if __name__ == '__main__':
    unittest.main()
