import shlex
from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
from twisted.plugin import IPlugin
from twisted.web.http import Request
from gitdaemon.git import findGitShell, findGitHTTPBackend
from zope.interface import implements
from gitdaemon.interfaces import IInvocationRequest, IInvocationRequestHandler, IRepositoryRouter
from gitdaemon.shared.user import User

class InvocationRequest(object):

    def __init__(self, proto, user, env = {}, args = []):
        self.proto = proto
        self.user = user
        self.env = env
        self.args = args
        self.repoPath = []

        assert self.invariant()

    def getProtocol(self):
        assert self.invariant()

        return self.proto
    
    def getRepositoryPath(self):
        assert self.invariant()

        return self.repoPath

    def getUser(self):
        assert self.invariant()

        return self.user

    def invariant(self):
        return  isinstance(self.proto, ProcessProtocol) and \
                isinstance(self.user, User) and \
                isinstance(self.repoPath, list) and \
                isinstance(self.env, dict) and \
                isinstance(self.args, list)

class HTTPInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    gitHTTPBackend = findGitHTTPBackend()

    def __init__(self, request, proto, user, env = {}, args = []):
        assert isinstance(request, Request)
        assert isinstance(proto, ProcessProtocol)
        assert isinstance(user, User)

        self.request = request

        InvocationRequest.__init__(self, proto, user, env, args);

        self.repoPath = request.prepath[:-1]

        assert self.invariant()

    def invocate(self, repository):
        assert isinstance(repository, str)

        assert self.invariant()

        self.env['SCRIPT_FILENAME'] = self.gitHTTPBackend
        self.env['GIT_PROJECT_ROOT'] = repository
        self.env['PATH_INFO'] = "/" + "/".join(self.request.prepath[-1:])
        self.env['REMOTE_USER'] = 'christophe'
        self.env['GIT_HTTP_EXPORT_ALL'] = '1'

        #print env['GIT_PROJECT_ROOT']
        #print env['PATH_INFO']

        reactor.spawnProcess(self.proto, self.gitHTTPBackend, [self.gitHTTPBackend] + self.args, self.env)

        assert self.invariant()

    def invariant(self):
        return  InvocationRequest.invariant(self) and \
                isinstance(self.request, Request)

class SSHInvocationRequest(InvocationRequest):
    implements(IInvocationRequest)

    gitShell = findGitShell()

    def __init__(self, request, proto, user, env = {}, args = []):
        argv = shlex.split(request)
        self.command = argv[0]

        InvocationRequest.__init__(self, proto, user, env, args);

        self.repoPath = argv[-1].split('/')

        assert self.invariant()

    def invocate(self, repository):
        assert isinstance(repository, str)

        assert self.invariant()

        env = {}
        command = self.command + ' ' + "'{0}'".format(repository)

        reactor.spawnProcess(self.proto, self.gitShell, (self.gitShell, '-c', command), env)

        assert self.invariant()

    def invariant(self):
        return  InvocationRequest.invariant(self) and \
                isinstance(self.command, str)

class InvocationRequestHandler(object):
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    _repositoryRouter = None

    def attachRouter(self, router):
        assert self._repositoryRouter == None
        assert IRepositoryRouter.providedBy(router)

        self._repositoryRouter = router

    def handle(self, request):
        assert IRepositoryRouter.providedBy(self._repositoryRouter)
        assert IInvocationRequest.providedBy(request)

        repository = self._repositoryRouter.route(request.getRepositoryPath())

        if repository != None:
            request.invocate(repository)
        else:
            raise Exception("Not a valid repo")

    def createHTTPInvocationRequest(self, request, proto, user, env, qargs = {}):
        assert(isinstance(request, Request))
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(user, User))
        assert(isinstance(env, dict))
        assert(isinstance(qargs, list) or isinstance(qargs, str))

        request = HTTPInvocationRequest(request, proto, user, env, qargs)

        assert(isinstance(request, InvocationRequest))

        return request

    def createSSHInvocationRequest(self, request, proto, user):
        assert(isinstance(request, str))
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(user, User))

        request = SSHInvocationRequest(request, proto, user)

        assert(isinstance(request, InvocationRequest))

        return request

invocationRequestHandler = InvocationRequestHandler()