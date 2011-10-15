from zope.interface import Interface

class GitRequest(Interface):

    """The main invocation logic when handling a Git request"""

    def handle(self):
        """Handle a request through Git"""

class GitAuthentication(Interface):

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