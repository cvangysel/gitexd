import os
import shlex
import string
from twisted.internet import reactor
import sys
from git import findGitShell, findGitHTTPBackend
import interface
from zope.interface import implements
from config import config

class BaseSSHExecutionMechanism:
    implements(interface.IExecutionMechanism)

    gitShell = findGitShell()

    def execute(self, proto, command, repository):
        env = {}
        command = command + ' ' + "'{0}'".format(repository)

        reactor.spawnProcess(proto, self.gitShell, (self.gitShell, '-c', command), env)

class BaseHTTPExecutionMechanism:
    implements(interface.IExecutionMechanism)

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
        if not interface.IExecutionMechanism.providedBy(self.executionMechanism):
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
    implements(interface.IInvocationRequest)

    executionMechanism = BaseHTTPExecutionMechanism()

    def __init__(self, request, proto):
        BaseInvocationRequest.__init__(self, proto);

        self.repoPath = request.prepath[:-1]
        self.command = request

        self.command.request = self.command.prepath[-1:]

class BaseSSHInvocationRequest(BaseInvocationRequest):
    implements(interface.IInvocationRequest)

    executionMechanism = BaseSSHExecutionMechanism()

    def __init__(self, request, proto):
        BaseInvocationRequest.__init__(self, proto);

        argv = shlex.split(request)

        self.repoPath = argv[-1].split('/')
        self.command = argv[0]

class BaseRepositoryRouter:
    implements(interface.IRepositoryRouter)

    def route(self, repository):
        schemePath = config.get("GitDaemon", "repositoryBasePath")
        path = os.path.join(schemePath, *repository)

        if not os.path.exists(path):
            print "Repo " + path + " does not exist on disk"

            return None
            # Do protocol independent error stuff

        return path

class BaseInvocationRequestHandler:
    implements(interface.IInvocationRequestHandler)

    """The main invocation logic when handling a Git request"""

    HTTPInvocationRequest = BaseHTTPInvocationRequest
    SSHInvocationRequest = BaseSSHInvocationRequest

    RepositoryRouter = BaseRepositoryRouter

    def __init__(self):
        self.repositoryRouter = self.RepositoryRouter()

    def handle(self, request):
        if not interface.IInvocationRequest.providedBy(request):
            raise Exception("Handle this")

        repository = self.repositoryRouter.route(request.getRepositoryPath())

        if not repository == None:
            request.getExecutionMechanism().execute(request.getProtocol(), request.getCommand(), repository)