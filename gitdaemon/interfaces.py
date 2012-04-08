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

    def handle(self, app, request):
        """Handle a request through Git"""

    def createHTTPInvocationRequest(self, request, proto, user, env):
        """Create an instance of IInvocationRequest that handles HTTP requests."""

    def createSSHInvocationRequest(self, request, proto, user):
        """Create an instance of IInvocationRequest that handles SSH requests."""

class IRepositoryRouter(Interface):

    def route(self, app, repository):
        "Returns an absolute path to the repository"

class IAuth(Interface):

    UserInterface = Attribute("The interface the object representing a user session implements")

    """The authentication and authorization logic"""

    def allowAnonymousAccess(self, app):
        """Whether or not anonymous access to the daemon is allowed"""

    def authenticateKey(self, app, credentials):
        """Authentication based on keys"""

    def authenticatePassword(self, app, credentials):
        """Authentication based on username and password"""

    def authorizeRepository(self, app, user, repository, readOnly):
        """Whether or not the user may access the repository"""

    def authorizeAdvertisement(self, user, advertisement):
        """
                This method gets a chance to make changes to the advertisement exposed
                by the Git process that handles communication with the repository.
              """

    def authorizeRequest(self, user, request):
        """
                This method gets a chance to make changes to the request made by the client.
              """

class IExceptionHandler(Interface):

    """Handles Exceptions of the IException class"""

    def handle(self, exception, proto = None):
        """Handles exceptions"""

class IException(Interface):

    """Represents an exception that's passed to the ErrorHandler"""

    def getMessage(self):
        """Returns a string indicating the exception."""

    def getProtocol(self):
        """Returns the protocol instance this exception occured in."""