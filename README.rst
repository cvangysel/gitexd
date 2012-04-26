Extensible Git Daemon
=====================

Extensible Git Daemon (*gitexd*) is an event-driven, customizable and extensible solution developed in Python for the purpose of a bachelor thesis at the University of Antwerp. It provides users with a basic daemon that exposes repositories through the Secure Shell and the Hypertext Transport Transfer Protocol.

The logic that the daemon uses to
	* route requested repositories to the local file system,
	* authenticate users,
	* authorize users,
	* handle errors,
	* and to invoke everything above
is customizable by the user of the daemon and thus allows for pretty advanced uses.

Requirements
------------
	* `Python 2.7 <http://www.python.org>`_
	* `Twisted 12.0.0 <http://www.twistedmatrix.com>`_
	
Using the daemon
----------------

Starting the daemon can be done as simply as the following code snippet:

.. code-block:: python

	config = ConfigParser.ConfigParser()
	config.readfp(open(‘gitexd.cfg’))
	
	pluginPackages = {
		IAuth: gitexd.plugins,
		IRepositoryRouter: gitexd.plugins
	}
	
	factory = Factory(config, pluginPackages)
	
	ssh = reactor.listenTCP(22, factory.createSSHFactory())
	http = reactor.listenTCP(80, factory.createHTTPFactory())
	
See the documentation for more information.
