from twisted.internet.interfaces import IProcessProtocol, ITransport, IProcessTransport
from twisted.internet.protocol import ProcessProtocol
from zope.interface import implements
from gitdaemon.protocol.authorization import GitDecoder, _stripHeaders

PUSH, PULL = range(0, 2)

class GitProcessProtocol(object):
    implements(IProcessProtocol, ITransport)

    def __init__(self, proto):
        assert isinstance(proto, ProcessProtocol)

        self._proto = proto
        self._decoder = GitDecoder("DAEMON")
        self._processDecoder = GitDecoder("CLIENT")

    def makeConnection(self, process):
        self._proto.makeConnection(_GitProcessTransport(process, self._processDecoder))

    def childDataReceived(self, childFD, data):
        """
                    Each line starts with a four byte line length declaration in hex.
                    The section is terminated by a line length declaration of 0000.
              """

        striped, data = _stripHeaders(data)

        if striped is not None:
            self._proto.childDataReceived(childFD, striped)

            if 'x-git-upload-pack-result' in striped or 'x-git-receive-pack-result' in striped:

                self._decoder.allowAll()
                self._processDecoder.allowAll()

        for x in self._decoder.process(data):
            self._proto.childDataReceived(childFD, x)

    def childConnectionLost(self, childFD):
        self._proto.childConnectionLost(childFD)

    def processExited(self, reason):
        self._proto.processExited(reason)

    def processEnded(self, reason):
        self._proto.processEnded(reason)

    def write(self, data):
        if self._proto.transport is not None:
            self._proto.transport.write(data)

    def writeSequence(self, seq):
        self.write(''.join(seq))

    def loseConnection(self):
        if self._proto.transport is not None:
            self._proto.transport.loseConnection();


class _GitProcessTransport(object):
    implements(IProcessTransport)

    def __init__(self, transport, decoder):
        assert ITransport.providedBy(transport)
        assert isinstance(decoder, GitDecoder)

        self._transport = transport
        self._decoder = decoder

    def closeStdin(self):
        self._transport.closeStdin()

    def closeStdout(self):
        self._transport.closeStdout()

    def closeChildFD(self, descriptor):
        self._transport.closeChildFD(descriptor)

    def writeToChild(self, childFd, data):
        self._transport.writeToChild(childFd, data)

    def loseConnection(self):
        self._transport.loseConnection()

    def signalProcess(self, signalID):
        self._transport.signalProcess(signalID)

    def write(self, data):
        for x in self._decoder.process(data):
            self._transport.write(x)

    def writeSequence(self, data):
        self._transport.writeSequence(data)

    def getPeer(self):
        return self._transport.getPeer()

    def getHost(self):
        return self._transport.getHost()