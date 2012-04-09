API Documentation
*****************

This page contains documentation about how to use the plugin infrastructure of the Git-Daemon project. This
makes extensive use of the Twisted Plugin System, to understand this completly please refer to the documentation
on the Twisted website at `The Twisted Plugin System <http://twistedmatrix.com/documents/current/core/howto/plugin.html>`_.

Getting started with the :mod:`gitdaemon` framework
===================================================

.. module:: gitdaemon

The whole point of this project is to implement a daemon that offers Git repositories over the HTTP and SSH
protocols and whilst being able to provide custom authentication, authorization, repository routing, error handling
and invocation logic.

Starting the daemon can be done as simply as the following code snippet:

.. code-block:: python

	config = ConfigParser.ConfigParser()
	config.readfp(open(‘gitdaemon.cfg’))
	
	pluginPackages = {
		IAuth: gitdaemon.plugins,
		IRepositoryRouter: gitdaemon.plugins
	}
	
	app = Application(config, pluginPackages)
	
	ssh = reactor.listenTCP(22, app.createSSHFactory())
	http = reactor.listenTCP(80, app.createHTTPFactory())
	
Where :mod:`gitdaemon.plugins` can be replaced by your custom plugin packages that you will be able to implement
after reading this page. Ideally one can use the Twisted Application Framework, see http://twistedmatrix.com/documents/current/core/howto/application.html,
and deploy your application using *.tac* files and *twistd*.

.. note::

	When using this framework in a production environment it is recommended that you run Python in **optimized** mode.
	:mod:`gitdaemon` makes extensive use of the *assert* statement and this can potentially slow down your application.
	
Implementing your own plugin packages
=====================================

.. automodule:: gitdaemon.interfaces

.. autointerface:: IAuth
	:members:
.. autointerface:: IRepositoryRouter
	:members:
.. autointerface:: IExceptionHandler
	:members:
.. autointerface:: IInvocationRequestHandler
	:members:
	
About the protocols
-------------------

.. automodule:: gitdaemon.protocol.ssh

.. auotmodule:: gitdaemon.protocol.http
