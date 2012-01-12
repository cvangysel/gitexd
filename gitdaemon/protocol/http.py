from twisted.web.http import Request
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from gitdaemon import Object
from gitdaemon.interfaces import IInvocationRequestHandler
from gitdaemon.shared.user import User

class GitHTTP(CGIScript, Object):

    isLeaf = False

    children = ()

    def __init__(self, app, user):
        self.user = user

        Object.__init__(self, app)
        CGIScript.__init__(self, None)

        self._invariant()

    def getChild(self, name, request):
        self._invariant()

        return GitHTTP(self.app, self.user)

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

        assert isinstance(self.user, User)
        assert not self.isLeaf
        assert not self.children