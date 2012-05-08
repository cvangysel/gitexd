"""
    The Hypertext Transfer Protocol offers authentication anonymously or through a password mechanism. For encryption one should inspect the
    secure variety of HTTP. However it is the responsibility of the user to launch the daemon using the correct structures provided by Twisted, see
    `Using SSL in Twisted <http://twistedmatrix.com/documents/current/core/howto/ssl.html>`.

    Client requests are GET requests to the web server and the plugin that implements the IRequestHandler interface should handle them correctly.
    As opposed to the persistent nature of Secure Shell where every request refers to a new session that exists for as long as there is something to be
    done, the Hypertext Transfer Protocol is stateless and one Git push or pull will take multiple requests through the daemon.

    When implementing users should be aware of this as authentication will happen for every individual HTTP request and it is currently not possible
    to keep a persistent state between individual HTTP requests (such as the daemon sees them). One should not worry about authorization as
    requests that have not been authorized are simply not allowed to pass..
"""

import copy
from twisted.web import http, resource
from twisted.web._auth.basic import BasicCredentialFactory
from twisted.web._auth.wrapper import HTTPAuthSessionWrapper
from twisted.web.server import Site
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from zope.interface.interface import Interface
from gitexd import Object
from gitexd.protocol import GitProcessProtocol

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

    def __init__(self, app, session):
        self._session = session

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

        self.app.getRequestHandler().handle(self.app, self.app.getRequestHandler().createHTTPRequest(self.app, request, proto, self._session, env))

        self._invariant()

    def _invariant(self):
        Object._invariant(self)

        if self.app.getAuth().SessionInterface is Interface:
            assert self.app.getAuth().SessionInterface.providedBy(self._session)

        assert not self.isLeaf
        assert not self.children