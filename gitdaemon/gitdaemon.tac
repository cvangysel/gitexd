from ConfigParser import ConfigParser
from twisted.application.service import Application
from twisted.application.internet import TCPServer

import gitdaemon

application = Application("GitDaemon") # Create the application

config = ConfigParser({'repositoryBasePath': '/home/christophe/Desktop/repositories'})
git = gitdaemon.Application(config)

sshService = TCPServer(2222, git.createSSHFactory(), 50, '127.0.0.1')
httpService = TCPServer(8080, git.createHTTPFactory(), 50, '127.0.0.1')

sshService.setServiceParent(application)
httpService.setServiceParent(application)