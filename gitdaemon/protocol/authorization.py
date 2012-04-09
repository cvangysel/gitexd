from twisted.internet import reactor
from twisted.internet.interfaces import IProcessProtocol
from twisted.python.failure import Failure
from gitdaemon.protocol.error import GitError
from gitdaemon.protocol.git import formatPackline

class UnauthorizedException(GitError):

    def __init__(self, proto):
        GitError.__init__(self, "You don't have access to this repository.", proto)

def authorizationErrorHandler(fail, app, proto):
    # TODO Possibly combine with authenticationErrorHandler
    from gitdaemon import Application

    assert isinstance(fail, Failure)
    assert isinstance(app, Application)
    assert IProcessProtocol.providedBy(proto)

    r = fail.trap(GitError, NotImplementedError, Exception)

    if r == GitError:
        """Pass to the ExceptionHandler"""

        app.getErrorHandler().handle(fail.value, proto)
    elif r == NotImplementedError:
        """NotImplemented, sometimes used for testing."""

        print fail

        fail.printTraceback()
        reactor.stop()
    else:
        """Unknown exception, halt excecution."""

        print fail

        fail.printTraceback()
        reactor.stop()

def _decodeGitList(raw):
    assert isinstance(raw, str)

    data = []
    x = 0

    while (x < len(raw)):
        length = int(raw[x:x+4], 16)

        if length > 0:
            data.append(raw[x+4:x+length].rstrip().replace('\x00', '').split(' '))
        elif length == 0:
            length = 4

        x += length

    assert isinstance(data, list)

    return data

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

class GitDecoder(object):

    def __init__(self, name):
        self._name = name

        self._advertisement = None

        self._ignore = False

        self._formatted = []
        self._decoded = []
        self._raw = ""

    def process(self, data):
        self._raw = self._raw + data

        if not self._ignore:
            self._decoded.extend(self._decodeGit())

            for x in self._process():
                yield x

        if self._ignore:
            if len(self._raw):
                yield self._raw

                self._raw = ""

    def _process(self):
        request = []

        cutOff = 0

        for i in range(len(self._decoded)):
            line = self._decoded[i]

            if line == "" or line[:4] == "done":
                value = None if not len(line) else line
                request.append(value)

                for x in self._processRequest(request):
                    yield x

                self._formatted.append(request)

                request = []

                cutOff = i + 1
            else:
                request.append(line)

        self._decoded = self._decoded[cutOff:]

    def _processRequest(self, request):
        if request[0][0] == '#':
            """"""
        elif request[0][0] == '\x01':
            """"""
        elif request[0][:3] == "NAK":
            """"""
        elif request[0][:4] == "PACK":
            """"""
        elif len(request[0]) > 32:
            #print self._name, "Advertisement", request
            if self._advertisement is None:
                self._advertisement = request
                self.allowAll()
        else:
            """"""

        for x in _formatRequest(request):
            yield x

    def _decodeGit(self):
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

    def allowAll(self):
        self._ignore = True

