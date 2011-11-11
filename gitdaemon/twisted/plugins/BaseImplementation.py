import os
import shlex
from twisted.internet import reactor
from twisted.plugin import IPlugin
from gitdaemon.git import findGitShell, findGitHTTPBackend
from gitdaemon.interfaces import *
from zope.interface import implements
from gitdaemon.config import config

class BaseAuthentication:
    implements(IAuthentication)

    def authenticateKey(self, key, credentials):
        return True

    def authenticatePassword(self, user, password):
        return True

class BaseSSHExecutionMechanism:
    implements(IExecutionMechanism)

    gitShell = findGitShell()

    def execute(self, proto, command, repository):
        env = {}
        command = command + ' ' + "'{0}'".format(repository)

        reactor.spawnProcess(proto, self.gitShell, (self.gitShell, '-c', command), env)

class BaseHTTPExecutionMechanism:
    implements(IExecutionMechanism)

    gitHTTPBackend = findGitHTTPBackend()
    
    def execute(self, proto, command, repository):
        env = command.env

        print command.qargs

        env['SCRIPT_FILENAME'] = self.gitHTTPBackend
        env['GIT_PROJECT_ROOT'] = repository
        env['PATH_INFO'] = "/" + "/".join(command.request)
        env['REMOTE_USER'] = 'christophe'
        env['GIT_HTTP_EXPORT_ALL'] = '1'

        print env['GIT_PROJECT_ROOT']
        print env['PATH_INFO']

        reactor.spawnProcess(proto, self.gitHTTPBackend, [self.gitHTTPBackend] + command.qargs, env)

class BaseInvocationRequest:

    def __init__(self, proto):
        if not IExecutionMechanism.providedBy(self.executionMechanism):
            raise Exception("Handle this")

        self.proto = proto

    def getProtocol(self):
        return self.proto
    
    def getRepositoryPath(self):
        return self.repoPath

    def getExecutionMechanism(self):
        return self.executionMechanism

    def getCommand(self):
        return self.command

class BaseHTTPInvocationRequest(BaseInvocationRequest):
    implements(IInvocationRequest)

    executionMechanism = BaseHTTPExecutionMechanism()

    def __init__(self, request, proto):
        BaseInvocationRequest.__init__(self, proto);

        self.repoPath = request.prepath[:-1]
        self.command = request

        self.command.request = self.command.prepath[-1:]

class BaseSSHInvocationRequest(BaseInvocationRequest):
    implements(IInvocationRequest)

    executionMechanism = BaseSSHExecutionMechanism()

    def __init__(self, request, proto):
        BaseInvocationRequest.__init__(self, proto);

        argv = shlex.split(request)

        self.repoPath = argv[-1].split('/')
        self.command = argv[0]

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

    HTTPInvocationRequest = BaseHTTPInvocationRequest
    SSHInvocationRequest = BaseSSHInvocationRequest

    RepositoryRouter = BaseRepositoryRouter()

    Authentication = BaseAuthentication()

    def handle(self, request):
        if not IInvocationRequest.providedBy(request):
            raise Exception("Handle this")

        repository = self.RepositoryRouter.route(request.getRepositoryPath())

        if repository != None:
            request.getExecutionMechanism().execute(request.getProtocol(), request.getCommand(), repository)
        else:
            raise Exception("Not a valid repo")

baseInvocationRequestHandler = BaseInvocationRequestHandler()