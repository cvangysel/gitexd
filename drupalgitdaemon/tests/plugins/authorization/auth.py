from twisted.plugin import IPlugin
from zope.interface.declarations import implements
from drupalgitdaemon.plugins.auth import DrupalAuth
from drupalgitdaemon.tests.plugins import DummyServiceProtocol
from gitdaemon.interfaces import IAuth

"""
    The following class copies the exact same behavior of DrupalAuth,
    the only difference is that it uses the DummyServiceProtocol.
"""

class DrupalTestAuth(DrupalAuth):
    implements(IPlugin, IAuth)

    def __init__(self):
        self.protocol = DummyServiceProtocol

auth = DrupalTestAuth()