from zope.interface import Interface
from zope.interface.interface import Attribute

class IExecutionMechanism(Interface):

    def execute(self, proto, command, repository):
        """Executes shizzle"""

class IInvocationRequest(Interface):

    """A request that came in through HTTP or SSH"""

    executionMechanism = Attribute("Implementation of IExecutionMechanism")

    def __init__(self, request, proto):
        """Handle it"""
        
    def getRepositoryPath(self):
        """Return the path to the requested repository"""

    def getProtocol(self):
        """Return the protocol the request originates from"""

    def getCommand(self):
        """Returns the command that needs to be executed"""

    def getExecutionMechanism(self):
        """Return an instance of the execution mechanism used by this kind of request"""

class IInvocationRequestHandler(Interface):
    """The main invocation logic when handling a Git request"""

    SSHInvocationRequest = Attribute("Implementation of IInvocationRequest for SSH protocol")
    HTTPInvocationRequest = Attribute("Implementation of IInvocationRequest for HTTP protocol")

    RepositoryRouter = Attribute("Implementation of IRepositoryRouter")

    def handle(self, request):
        """Handle a request through Git"""

class IRepositoryRouter(Interface):

    def route(self, repository):
        "Returns an absolute path to the repository"

class IAuthorization(Interface):

    """The authentication logic"""

    def authenticate(self, request):

        """Authenticate the current request, returns True of False"""

class GitError(Interface):

    """An error encapsulation for Git errors"""
    
    def invoke(self, request):

        """When the error is thrown"""

class GitRepository(Interface):

    """Encapsulation for Git repositories, mainly focusses on routing to the repository"""

    def __init__(self, repository):

        """Initialize the repository object and route it to the correct directory"""