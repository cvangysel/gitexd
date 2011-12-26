import os
import shlex
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ProcessProtocol
from twisted.plugin import IPlugin
from twisted.web.http import Request
from gitdaemon.git import findGitShell, findGitHTTPBackend
from gitdaemon.interfaces import *
from zope.interface import implements
from gitdaemon.config import config
from gitdaemon.shared.user import User

class BaseAuthentication:
    implements(IAuthentication)

    def authenticateKey(self, key, credentials):
        return True

    def authenticatePassword(self, user, password):
        return True

class BaseInvocationRequest:

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

class BaseHTTPInvocationRequest(BaseInvocationRequest):
    implements(IInvocationRequest)

    gitHTTPBackend = findGitHTTPBackend()

    def __init__(self, request, proto, user, env = {}, args = []):
        assert isinstance(request, Request)
        assert isinstance(proto, ProcessProtocol)
        assert isinstance(user, User)

        self.request = request

        BaseInvocationRequest.__init__(self, proto, user, env, args);

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
        return  BaseInvocationRequest.invariant(self) and \
                isinstance(self.request, Request)

class BaseSSHInvocationRequest(BaseInvocationRequest):
    implements(IInvocationRequest)

    gitShell = findGitShell()

    def __init__(self, request, proto, user, env = {}, args = []):
        argv = shlex.split(request)
        self.command = argv[0]

        BaseInvocationRequest.__init__(self, proto, user, env, args);

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
        return  BaseInvocationRequest.invariant(self) and \
                isinstance(self.command, str)

class BaseRepositoryRouter:
    implements(IRepositoryRouter)

    def route(self, repository):
        schemePath = config.get("GitDaemon", "repositoryBasePath")
        path = os.path.join(schemePath, *repository)

        if not os.path.exists(path):
            print "Repo " + path + " does not exist on disk"

            return None
            # Do protocol independent error stuff

        return path

class BaseInvocationRequestHandler:
    implements(IPlugin, IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    RepositoryRouter = BaseRepositoryRouter()

    Authentication = BaseAuthentication()

    def handle(self, request):
        assert IInvocationRequest.providedBy(request)

        repository = self.RepositoryRouter.route(request.getRepositoryPath())

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

        request = BaseHTTPInvocationRequest(request, proto, user, env, qargs)

        assert(isinstance(request, BaseInvocationRequest))

        return request

    def createSSHInvocationRequest(self, request, proto, user):
        assert(isinstance(request, str))
        assert(isinstance(proto, ProcessProtocol))
        assert(isinstance(user, User))

        request = BaseSSHInvocationRequest(request, proto, user)

        assert(isinstance(request, BaseInvocationRequest))

        return request

baseInvocationRequestHandler = BaseInvocationRequestHandler()