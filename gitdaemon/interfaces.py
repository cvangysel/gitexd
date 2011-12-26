from zope.interface import Interface
from zope.interface.interface import Attribute

class IInvocationRequest(Interface):

    """A request that came in through HTTP or SSH"""

    def __init__(self, request, proto, env = {}, args = []):
        """Handle it"""
        
    def getRepositoryPath(self):
        """Return the path to the requested repository"""

    def getProtocol(self):
        """Return the protocol the request originates from"""

    def getUser(self):
        """Return the user that invocated the request"""

    def invocate(self):
        """Show time"""

class IInvocationRequestHandler(Interface):
    """The main invocation logic when handling a Git request"""

    RepositoryRouter = Attribute("Instantation of a implementation of IRepositoryRouter")

    Authentication = Attribute("Instantation of a implementation of IAuthentication")

    def handle(self, request, user):
        """Handle a request through Git"""

    def createHTTPInvocationRequest(self, request, proto, user, env, qargs = {}):
        """Create an instance of IInvocationRequest that handles HTTP requests."""

    def createSSHInvocationRequest(self, request, proto, user):
        """Create an instance of IInvocationRequest that handles SSH requests."""

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
