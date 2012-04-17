"""
    Fix me.
"""

import copy
from twisted.web import http, resource
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from zope.interface.interface import Interface
from gitdaemon import Object
from gitdaemon.protocol import GitProcessProtocol

class GitProcessProtocol(GitProcessProtocol):
    """
            Custom implementation to support error messages.
       """

    def die(self, message):
        if self._processTransport is None:
            self._proto.request.setResponseCode(500)
            self._proto.request.unregisterProducer()
            self._proto.request.finish()
        else:
            self._die()

    def processEnded(self, reason):
        if self._dead:
            self._proto.request.write(resource.ErrorPage(http.INTERNAL_SERVER_ERROR, "CGI Script Error", "There was an error.").render(self._proto.request))

        self._proto.request.unregisterProducer()
        self._proto.request.finish()

class Factory(Site):

    def __init__(self, portal, config):
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
        assert(isinstance(request, http.Request))
        assert(isinstance(env, dict))

        self._invariant()

        proto = CGIProcessProtocol(request)

        self.app.getRequestHandler().handle(self.app, self.app.getRequestHandler().createHTTPRequest(self.app, request, proto, self.user, env))

        self._invariant()

    def _invariant(self):
        Object._invariant(self)

        if self.app.getAuth().UserInterface is Interface:
            assert self.app.getAuth().UserInterface.providedBy(self.user)

        assert not self.isLeaf
        assert not self.children