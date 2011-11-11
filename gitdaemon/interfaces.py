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

    def getUser(self):
        """Return the user that invocated the request"""

class IInvocationRequestHandler(Interface):
    """The main invocation logic when handling a Git request"""

    SSHInvocationRequest = Attribute("Implementation of IInvocationRequest for SSH protocol")
    HTTPInvocationRequest = Attribute("Implementation of IInvocationRequest for HTTP protocol")

    RepositoryRouter = Attribute("Instantation of a implementation of IRepositoryRouter")

    Authentication = Attribute("Instantation of a implementation of IAuthentication")

    def handle(self, request, user):
        """Handle a request through Git"""

class IRepositoryRouter(Interface):

    def route(self, repository):
        "Returns an absolute path to the repository"

class IAuthentication(Interface):

    """The authentication logic"""

    def authenticateKey(self, key, credentials):

        """Authentication based on keys"""

    def authenticatePassword(self, user, password):

        """Authentication based on username and password"""

class GitError(Interface):

    """An error encapsulation for Git errors"""
    
    def invoke(self, request):

        """When the error is thrown"""

class GitRepository(Interface):

    """Encapsulation for Git repositories, mainly focusses on routing to the repository"""

    def __init__(self, repository):

        """Initialize the repository object and route it to the correct directory"""