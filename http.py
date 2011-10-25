from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.twcgi import CGIScript, CGIProcessProtocol
from interface import IInvocationRequestHandler

class GitHTTP(CGIScript):

    isLeaf = False

    children = []

    def __init__(self, requestHandler):
        CGIScript.__init__(self, None)
        self.requestHandler = requestHandler

    def getChild(self, name, request):
        return GitHTTP(self.requestHandler)

    def runProcess(self, env, request, qargs = {}):
        if IInvocationRequestHandler.providedBy(self.requestHandler):
            proto = CGIProcessProtocol(request)

            request.env = env
            request.qargs = qargs

            self.requestHandler.handle(self.requestHandler.HTTPInvocationRequest(request, proto))
        else:
            raise Exception("requestHandler does not implement correct interface")