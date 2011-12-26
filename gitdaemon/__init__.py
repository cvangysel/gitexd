import sys
from twisted.python import log

log.startLogging(sys.stderr)

print "HAHAHAHAHAHa"
#__path__.extend(pluginPackagePaths(__name__))
#sys.path.append("/home/christophe/Desktop/Git-Daemon/gitdaemon")
sys.path.append("/home/christophe/Desktop/Git-Daemon")
#__all__ = []

print sys.path

print __path__
print __name__