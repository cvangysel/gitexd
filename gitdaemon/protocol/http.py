from twisted.web.http import Request
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from gitdaemon.interfaces import IInvocationRequestHandler
from gitdaemon.shared.user import User

class GitHTTP(CGIScript):

    isLeaf = False

    children = ()

    def __init__(self, requestHandler, user):
        CGIScript.__init__(self, None)

        self.requestHandler = requestHandler
        self.user = user

        assert self.invariant()

    def getChild(self, name, request):
        assert self.invariant()

        return GitHTTP(self.requestHandler, self.user)

    def runProcess(self, env, request, qargs = []):
        assert(isinstance(request, Request))
        assert(isinstance(env, dict))
        assert(isinstance(qargs, list) or isinstance(qargs, str))

        assert self.invariant()

        proto = CGIProcessProtocol(request)

        self.requestHandler.handle(self.requestHandler.createHTTPInvocationRequest(request, proto, self.user, env, qargs))

        assert self.invariant()

    def invariant(self):
        return IInvocationRequestHandler.providedBy(self.requestHandler) and \
                isinstance(self.user, User) and\
                not self.isLeaf and \
                not self.children