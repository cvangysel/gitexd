import copy
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.http import Request
from twisted.web.server import Site
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from zope.interface.interface import Interface
from gitdaemon import Object
from gitdaemon.protocol import GitProcessProtocol

class GitProcessProtocol(GitProcessProtocol):
    """
            Custom implementation to support error messages.
       """

    def write(self, data):
        self._proto.request.setResponseCode(500)
        self._proto.request.write(data)

    def writeSequence(self, seq):
        self.write(''.join(seq))

    def loseConnection(self):
        self._proto.request.unregisterProducer()
        self._proto.request.finish()

class Factory(Site):

    def __init__(self, portal, config):
        # TODO might want to use DigestCredentialFactory here
        Site.__init__(self, HTTPAuthSessionWrapper(portal, [BasicCredentialFactory("GitDaemon")]))

    def getResourceFor(self, request):
        request.site = self
        request.sitepath = copy.copy(request.prepath)

        request.prepath.extend(request.postpath)
        request.postpath = []

        return self.resource

class Script(CGIScript, Object):

    isLeaf = False

    children = ()

    def __init__(self, app, user):
        self.user = user

        Object.__init__(self, app)
        CGIScript.__init__(self, None)

        self._invariant()

    def getChild(self, name, request):
        raise NotImplementedError()

    def runProcess(self, env, request, qargs = []):
        assert(isinstance(request, Request))
        assert(isinstance(env, dict))

        self._invariant()

        proto = CGIProcessProtocol(request)

        self.app.getRequestHandler().handle(self.app, self.app.getRequestHandler().createHTTPInvocationRequest(request, proto, self.user, env))

        self._invariant()

    def _invariant(self):
        Object._invariant(self)

        if self.app.getAuth().UserInterface is Interface:
            assert self.app.getAuth().UserInterface.providedBy(self.user)

        assert not self.isLeaf
        assert not self.children