from ConfigParser import ConfigParser
from twisted.application.service import Application
from twisted.application.internet import TCPServer
from drupalgitdaemon import plugins
import gitdaemon
from gitdaemon.interfaces import IAuth, IExceptionHandler, IRepositoryRouter, IInvocationRequestHandler

application = Application("GitDaemon-DrupalOrg") # Create the application

config = ConfigParser(defaults = {
        "allowAnonymous": False,
	"repositoryPath": "/var/www/vhost/thesis/repositories",
	"privateKeyLocation": "/home/christophe/Desktop/Git-Daemon/gitdaemon/tests/example-key/key",
	"publicKeyLocation": "/home/christophe/Desktop/Git-Daemon/gitdaemon/tests/example-key/key.pub",
	"serviceUrl": "http://bachelorthesis/drupal/drupalorg/",
	"headers": ""
})

pluginPackages = {
    IAuth: plugins,
    IRepositoryRouter: plugins
}

git = gitdaemon.Application(config, pluginPackages)

sshService = TCPServer(2222, git.createSSHFactory(), 50, '127.0.0.1')
httpService = TCPServer(8080, git.createHTTPFactory(), 50, '127.0.0.1')

sshService.setServiceParent(application)
httpService.setServiceParent(application)
