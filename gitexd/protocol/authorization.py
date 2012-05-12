from twisted.internet import reactor, defer
from twisted.internet.interfaces import IProcessProtocol
from twisted.python.failure import Failure
from gitexd.protocol.error import GitError
from gitexd.protocol.git import formatPackline

class UnauthorizedRepositoryException(GitError):

    def __init__(self, proto):
        GitError.__init__(self, "You don't have access to this repository.", proto)

class UnauthorizedReferencesException(GitError):

    def __init__(self, proto):
        GitError.__init__(self, "You don't have access to this reference.", proto)

def authorizationErrorHandler(fail, app, proto):
    from gitexd import Factory

    assert isinstance(fail, Failure)
    assert isinstance(app, Factory)
    assert IProcessProtocol.providedBy(proto)

    r = fail.trap(GitError, Exception)

    if r == GitError:
        """Pass to the ExceptionHandler"""

        app.getErrorHandler().handle(fail.value, proto)
    else:
        """Unknown exception, halt excecution."""

        fail.printTraceback()
        reactor.stop()

def _consume(data, length):
    assert isinstance(data, str)

    if len(data) < length:
        return False

    part = data[:length]
    data = data[length:]

    return part, data

def _stripHeaders(data):
    assert isinstance(data, str)

    striped = None

    lastOccurence = data.rfind("\r\n")
    if lastOccurence >= 0:
        striped = data [:lastOccurence + 2]
        data = data[lastOccurence + 2:]

    return striped, data

def _formatRequests(requests):
    for request in requests:
        _formatRequest(request)

def _formatRequest(request):
    for i in request:
        if i is None:
            yield "0000"
        else:
            yield formatPackline(i)

def _isAdvertisement(request):
    if len(request) == 1 and request[0] is None:
        # Empty advertisement
        return True
    if request[0][0] == '#':
        """"""
    elif request[0][:3] == "NAK":
        """"""
    elif request[0][:4] == "PACK":
        """"""
    elif len(request[0]) > 32:
        return True
    else:
        """"""

    return False

class GitDecoder(object):

    def __init__(self):
        self._advertisementDeferred = defer.Deferred()

        self._accepted = False

        self._decoded = []
        self._raw = ""

        self._processed = []

    def getAdvertisementDeferred(self):
        return self._advertisementDeferred

    def accept(self):
        self._accepted = True

    def flush(self):
        if not self._accepted:
            requests = self._extractRequests()

            advertisement = None

            for request in requests:
                if _isAdvertisement(request):
                    advertisement = request
                    break

            self._processed.extend(requests)

            if advertisement is not None:
                self._advertisementDeferred.callback(advertisement)

        if self._accepted:
            for request in self._processed:
                for x in _formatRequest(request):
                    yield x

            self._processed = []

            if len(self._raw):
                yield self._raw

            self._raw = ""

    def decode(self, data):
        self._raw = self._raw + data

    def _extractRequests(self):
        self._decoded.extend(self._extractLines())

        requests = []
        request = []

        cutOff = 0

        for i in range(len(self._decoded)):
            line = self._decoded[i]

            if line == "" or line[:4] == "done":
                value = None if not len(line) else line
                request.append(value)

                requests.append(request)

                request = []

                cutOff = i + 1
            else:
                request.append(line)

        self._decoded = self._decoded[cutOff:]

        return requests

    def _extractLines(self):
        data = []

        while len(self._raw) > 0:
            result = _consume(self._raw, 4)

            if result:
                length, self._raw = result
            else:
                break

            try:
                length = int(length, 16)
            except ValueError:
                self._raw = length + self._raw
                break

            if not length:
                data.append("")
            else:
                result = _consume(self._raw, length - 4)

                if result:
                    line, self._raw = result

                    data.append(line)
                else:
                    break

        return data

    def isAccepted(self):
        self._accepted