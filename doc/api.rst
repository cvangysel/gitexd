API Documentation
*****************

This page contains documentation about how to use the plugin infrastructure of the `gitexd` project. The project
makes extensive use of the Twisted Plugin System, to understand this completly please refer to the documentation
on the Twisted website at `The Twisted Plugin System <http://twistedmatrix.com/documents/current/core/howto/plugin.html>`_.

Getting started with the :mod:`gitexd` framework
================================================

.. module:: gitexd

The whole point of this project is to implement a daemon that offers Git repositories over the HTTP and SSH
protocols and whilst being able to provide custom authentication, authorization, repository routing, error handling
and invocation logic.

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
	
Where :mod:`gitexd.plugins` can be replaced by your custom plugin packages that you will be able to implement
after reading this page. Ideally one can use the Twisted Application Framework, see http://twistedmatrix.com/documents/current/core/howto/application.html,
and deploy your application using *.tac* files and *twistd*.

.. note::

	When using this framework in a production environment it is recommended that you run Python in **optimized** mode.
	:mod:`gitexd` makes extensive use of the *assert* statement and this can potentially slow down your application.
	
Implementing your own plugin packages
-------------------------------------

.. automodule:: gitexd.interfaces

.. _SessionInterface:
Authentication and Authorization
++++++++++++++++++++++++++++++++

.. autointerface:: IAuth
	:members:
	
Repository Routing
++++++++++++++++++

.. autointerface:: IRepositoryRouter
	:members:
	
Exception Handling
++++++++++++++++++

.. autointerface:: IExceptionHandler
	:members:
	
Request Handling
++++++++++++++++

.. autointerface:: IRequestHandler
	:members:
	
.. autointerface:: IRequest
	:members:
	
.. _requesttype:
About the protocols
===================

.. automodule:: gitexd.protocol

The `SSH` transport protocol
----------------------------
.. automodule:: gitexd.protocol.ssh

The `HTTP` transport protocol
-----------------------------
.. automodule:: gitexd.protocol.http
