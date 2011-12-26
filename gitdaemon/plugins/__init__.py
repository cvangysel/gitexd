from twisted.plugin import pluginPackagePaths

__path__.extend(pluginPackagePaths(__name__))
__all__ = []

__author__ = 'christophe'

print __name__
print "trolol"