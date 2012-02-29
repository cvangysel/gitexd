from ConfigParser import ConfigParser
import os
from twisted.conch.error import ConchError
from twisted.internet import defer
from twisted.plugin import IPlugin
from twisted.trial import unittest
import urllib
from zope.interface.declarations import implements
from drupalgitdaemon.plugins.auth import DrupalAuth
from drupalgitdaemon.service import IServiceProtocol
from gitdaemon.interfaces import IAuth

class DummyServiceProtocol(object):
    implements(IServiceProtocol)

    def __init__(self, config, command):
        assert isinstance(config, ConfigParser)
        assert isinstance(command, str)

        self.command = command
        self.config = config

        self.deferred = None

    def request(self, *args):
        testFilePath = os.path.dirname(__file__) + "/testFiles/" + self.command

        filename = ""

        arguments = dict()
        for a in args:
            arguments.update(a)

        if arguments.has_key('username'):
            filename += "_user-" + arguments['username']

        if arguments.has_key('password'):
            filename += "_pass-" + arguments['password']

        if arguments.has_key('fingerprint'):
            filename += "_fingerprint-" + arguments['fingerprint']

        try:
            file = open(testFilePath + "/" + filename).read()
        except:
            self.deferred = defer.fail(NotImplementedError(testFilePath + "/" + filename))
        else:
            print "DummyProtocol", filename, "result: ", file

            self.deferred = defer.succeed(file)



class DummyError(ConchError):
    pass

"""
    The following class copies the exact same behavior of DrupalAuth,
    the only difference is that it uses the DummyServiceProtocol.
"""

class DrupalTestAuth(DrupalAuth):
    implements(IPlugin, IAuth)

    def __init__(self):
        self.protocol = DummyServiceProtocol

auth = DrupalTestAuth()