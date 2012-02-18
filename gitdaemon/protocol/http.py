import copy
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.http import Request
from twisted.web.server import Site
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from zope.interface.interface import Interface
from gitdaemon import Object

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
        assert(isinstance(qargs, list) or isinstance(qargs, str))

        self._invariant()

        proto = CGIProcessProtocol(request)

        self.app.getRequestHandler().handle(self.app, self.app.getRequestHandler().createHTTPInvocationRequest(request, proto, self.user, env, qargs))

        self._invariant()

    def _invariant(self):
        Object._invariant(self)

        if self.app.getAuth().UserInterface is Interface:
            assert self.app.getAuth().UserInterface.providedBy(self.user)

        assert not self.isLeaf
        assert not self.children