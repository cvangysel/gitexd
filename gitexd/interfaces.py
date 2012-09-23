"""
    The `interfaces` module contains all the interfaces you can implement to provide your own logic. However, it is not required to implement all of them.
    A cherry-pick approach can be used and most of the time only implementing :class:`IAuth` and :class:`IRepositoryRouter`
    can get you a long way. If you want to override the error messages or log them to some external service, have a look at :class:`IExceptionHandler`
    and if you don't like the order of invocation or want to experiment a little, check out :class:`IRequestHandler` and :class:`IRequest`.

    .. note::
        All other subsystems (except the authentication part of :class:`IAuth` and some error messages) are invoked by :class:`IRequestHandler` and
        :class:`IRequest`. I hope that you won't need to implement these, that would mean our approach wasn't sufficiently generic enough.

    The interface system is the same as used internally by Twisted, please refer to the documentation on the Twisted website at
    `Components: Interfaces and Adapters <http://twistedmatrix.com/documents/current/core/howto/components.html>`_.
"""

from zope.interface import Interface
from zope.interface.interface import Attribute

class IRequestHandler(Interface):
  """
    This interface provides the beating heart of the daemon and the basic implementation should suffice for most uses.
    Request enter from their respective protocol implementations through the `handle` method that takes care of them,
    each request is actually represented by the :class:`IRequest` interface.

    The handler also provides factory-like capabilities for creating :class:`IRequest` instances. Every request created through
    these methods has already been authenticated, but not authorized. They serve as an entry- and exit-point in the protocol-independent logic.

    .. note::
       Authentication happens on transport-layer level in the SSH and HTTP modules, therefore every request has been authenticated before
       there's a chance to interact with them.

    .. note::
       Error handling can happen in stages outside of the scope of the :class:`IRequestHandler`, for example during authentication.

    It is the responsibility of the :class:`IRequestHandler` interface to invoke the `IRequest.finish` method on the
    respective IRequest instances after the request has been routed and authorized.
  """

  def handle(self, factory, request):
    """Handle a Git request.

          Args:
              factory (:class:`Factory`):  The application object.
              request (:class:`IRequest`):  The request that needs to be handled.
    """

  def createHTTPRequest(self, request, protocol, session, env):
    """Create an instance of :class:`IRequest` that handles HTTP requests.

          Args:
              request (:class:`twisted.web.http.Request`): The HTTP request object created by Twisted.
              protocol (:class:`twisted.internet.protocol.ProcessProtocol`): The ProcessProtocol object representing the connection.
              session: Instance of the interface linked to by :ref:`SessionInterface`.
              env (dict): Environment variables.

          Returns:
              Instance of :class:`IRequest`.
    """

  def createSSHRequest(self, request, protocol, session):
    """Create an instance of :class:`IRequest` that handles SSH requests.

          Args:
              request (str): The command executed over the SSH transport protocol.
              protocol (:class:`twisted.internet.protocol.ProcessProtocol`): The ProcessProtocol object representing the connection.
              session: Instance of the interface linked to by :ref:`SessionInterface`.

          Returns:
              Instance of :class:`IRequest`.
    """


class IRequest(Interface):
  """
       This interface represents a request to the daemon and contains all the needed information to process that request.

       .. note::
           A new request is equal to a new connection, a single Git request through the HTTP protocol thus manifests itself as multiple
           :class:`IRequest`s. For more information see `About the protocols`_.
  """

  def getType(self):
    """Returns whether the request is a pull or push.

         Returns:
             int. `protocol.PULL` or `protocol.PUSH` values (see :ref:`requesttype`)  according to the type or request (read or write).
    """

  def getRepositoryPath(self):
    """Return the path to the requested repository. This still needs to be processed by the :class:`IRepositoryRouter` plugin.

          Returns:
              list or None.
    """

  def getProtocol(self):
    """Return the :class:`twisted.internet.protocol.ProcessProtocol` representing the connection."""

  def getSession(self):
    """Returns the instance of the interface linked to by :ref:`SessionInterface`."""

  def finish(self, repository):
    """Executes the request by accessing the requested repository and performing the appropriate actions. This often means that
       the connection is transferred to the correct Git process to handle the connection. If one wishes to hook a Python implementation of the
       `git-receive-pack` or `git-upload-pack` logic, this would be the place to do it.

       After this method executes the connection should be closed automatically.

          Args:
              repository (str): The routed repository the request should act upon.
    """


class IRepositoryRouter(Interface):
  """
       This interface defines a mapping between offered repositories and their location on the file system. This plugin is one of the most likely
       you will need to define yourself.
  """

  def route(self, factory, repository):
    """"Returns an absolute path to the repository on the file system. You best use the utilities in the `os.path` module
        to avoid problems on different operation systems. It should also ensure that the repository exists on the file system.

          Args:
              factory (:class:`Factory`):  The application object.
              repository (list): The requested repository.

          Returns:
              str or None. The path to the repository on the file system or None if the repository does not exist.
    """


class IAuth(Interface):
  """
       This interface when implemented should provide authentication through username, password and private key combinations,
       coarse-scaled authorization (repository-based) and fine-scaled authorization (label-based).

       You should provide the static SessionInterface attribute with an interface that will represent a session or user in
       your implementation.

       All the authentication-based methods should return an instantiation of this interface on success which will the be passed to the
       authorization-based methods when their time arrives. This allows every request to be represented by the implementer's choice of state,
       from as simple as storing the username to as complicated as making server-side request to a third party system.

       .. note::
           All the methods can also return a :class:`Deferred` that returns the appropriate values. This allows for an
           asynchronous execution model where the result of the request isn't available at the moment but will be in the future.

           For more information refer to the Twisted documentation at `Deferred Reference <http://twistedmatrix.com/documents/current/core/howto/defer.html>`_.

       .. note::
           Implementations of the interface provided by the implementer should provide a textual representation of the user that the request
           belongs to, this mean the __str__ method needs to be implemented. This representation is passed through to the server-side Git
           logic to use as a means to identify the name of the committer when pushing over the HTTP protocol.
  """

  SessionInterface = Attribute("An interface that represents a `session` in the implementation. " +
                               "It is mainly used to keep a persistent state between authentication and authorization.")

  def allowAnonymousAccess(self, factory):
    """Whether or not anonymous access to the service is allowed.

          Args:
              factory (:class:`Factory`):  The application object.

          Returns:
              Instance of :ref:`SessionInterface` implementation if successful, None or False otherwise. For example:.
                  None or False -- Anonymous access is not supported.
                  Instance of :ref:`SessionInterface` implementation -- Anonymous access is supported and the returned instance will be used for authorization.
    """

  def authenticateKey(self, factory, credentials):
    """Whether or not the specified :class:`ISSHPrivateKey` instance contains valid credentials.

          Args:
              factory (:class:`Factory`):  The application object.
              credentials (:class:`ISSHPrivateKey`): The credentials to verify.

          Returns:
              Instance of :ref:`SessionInterface` implementation if successful, None or False otherwise. For example:.
                  None or False -- Provided credentials are incorrect.
                  Instance of :ref:`SessionInterface` implementation -- Provided credentials are correct.
    """

  def authenticatePassword(self, factory, credentials):
    """Whether or not the specified :class:`IUsernamePassword` instance contains valid credentials.

          Args:
              factory (:class:`Factory`):  The application object.
              credentials (:class:`IUsernamePassword`): The credentials to verify.

          Returns:
              Instance of :ref:`SessionInterface` implementation if successful, None or False otherwise. For example:.
                  None or False -- Provided credentials are incorrect.
                  Instance of :ref:`SessionInterface` implementation -- Provided credentials are correct.
    """

  def authorizeRepository(self, session, repository, requestType):
    """Authorizes access to a certain repository (coarse-scaled authorization).

          Args:
              session: Instance of the interface linked to by :ref:`SessionInterface`.
              repository (str): Path to repository
              requestType (int): `protocol.PULL` or `protocol.PUSH` values (see :ref:`requesttype`) according to the type or request (read or write).

          Returns:
              bool. Depending on whether the request is authorized.
    """

  def authorizeReferences(self, session, refs, requestType):
    """Authorizes access to certain references in the current repository (fine-scaled authorization).

          Args:
              session: Instance of the interface linked to by :ref:`SessionInterface`.
              labels (list): Tuple of refs (list). The structure of these refs depend on the requestType.
                  - Push: each ref is actually a reference change with a previous reference, the next reference and a label name
                  - Pull: each ref has as a first value "want" or "have", followed by a reference
              requestType (int): `protocol.PULL` or `protocol.PUSH` values (see :ref:`requesttype`) according to the type or request (read or write).

          Returns
              bool. Depending on whether the request is authorized.
    """


class IExceptionHandler(Interface):
  """
       All error handling is done through the implementation of this interface. It's also the simplest of all interfaces described here and
       you will only need to implement it yourself if you want custom error messages, like translated messages for example, or you if you have
       the desire to log every error somewhere..
  """

  def handle(self, exception, protocol=None):
    """Handles the error, an instance of an implementation of :class:`IException`, and acts appropriately. This often means that the message
contained in the error is displayed to the user and that the connection is terminated.

This method can be invoked with an instance of :class:`twisted.internet.protocol.ProcessProtocol`, but it can also be contained in the
error itself or it just might not be available. This is because the object might not be available at the moment of error and you can't
exactly wait on it being created when stuff is going wrong. If there is no object at all, that's because the `Twisted` decided to terminate the
connection for us, and is kindly letting us know.

Args:
exception (:class:`IException`): Instance of implementation of :class:`IException` representing the error.

Kwargs:
protocol (:class:`twisted.internet.protocol.ProcessProtocol` or None): The ProcessProtocol object representing the connection."""


class IException(Interface):
  """Represents an exception that's passed to the ErrorHandler"""

  def getMessage(self):
    """Returns a string indicating the exception."""

  def getProtocol(self):
    """Returns the protocol instance this exception occured in."""