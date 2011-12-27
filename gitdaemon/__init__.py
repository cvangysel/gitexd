import sys
from twisted.plugin import IPlugin, getPlugins
from twisted.python import log

# hack to clear cache
list(getPlugins(IPlugin))