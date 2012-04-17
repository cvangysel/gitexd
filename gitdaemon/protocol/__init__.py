from twisted.internet import main
from twisted.internet.interfaces import IProcessProtocol, ITransport, IProcessTransport
from twisted.internet.protocol import ProcessProtocol
from twisted.python.failure import Failure
from zope.interface import implements
from gitdaemon.protocol.authorization import GitDecoder, _stripHeaders

PULL, PUSH = range(0, 2)

class GitProcessProtocol(object):
    implements(IProcessProtocol)

    def _authorizeLabelCallback(self, request):
        self._decoder.accept()
        self._flush()

    def __init__(self, proto, authCallback):
        assert isinstance(proto, ProcessProtocol)

        self._dead = False

        self._proto = proto
        self._decoder = GitDecoder()

        self._processTransport = None
        self._processTransportDecoder = GitDecoder()

        self._decoder.getAdvertisementDeferred().addCallback(self._authorizeLabelCallback)
        self._processTransportDecoder.getAdvertisementDeferred().addCallback(authCallback, self)

    def getRequestReceivedDeferred(self):
        return self._processTransportDecoder.getAdvertisementDeferred()

    def authorize(self):
        self._processTransportDecoder.accept()
        self._processTransport._flush()

    def die(self, message):
        if self._proto.transport is not None:
            self._proto.transport.write(message)
            self._proto.transport.loseConnection()

        self._die()

    def _die(self):
        self._processTransport._transport.loseConnection()
        self._dead = True

    def _flush(self):
        for x in self._decoder.flush():
            self._proto.childDataReceived(1, x)

    """
        Everthing that belongs to the IProcessProtocol interface.
    """

    def makeConnection(self, process):
        self._processTransport = _GitProcessTransport(process, self._processTransportDecoder)
        self._proto.makeConnection(self._processTransport)

    def childDataReceived(self, childFD, data):
        """
                    All the data received in this method is sent from the daemon to the client.
              """

        if childFD == 1:
            striped, data = _stripHeaders(data)

            if striped is not None:
                self._proto.childDataReceived(childFD, striped)

                if 'x-git-upload-pack-result' in striped or 'x-git-receive-pack-result' in striped:
                    self._decoder.accept()
                    self._processTransportDecoder.accept()

            self._decoder.decode(data)
            self._flush()
        else:
            self._proto.childDataReceived(childFD, data)

    def childConnectionLost(self, childFD):
        self._proto.childConnectionLost(childFD)

    def processExited(self, reason):
        self._proto.processExited(reason)

    def processEnded(self, reason):
        self._proto.processEnded(reason)

class _GitProcessTransport(object):
    implements(IProcessTransport)

    def __init__(self, transport, decoder):
        assert ITransport.providedBy(transport)
        assert isinstance(decoder, GitDecoder)

        self._transport = transport
        self._decoder = decoder

    def _flush(self):
        for x in self._decoder.flush():
            self._transport.write(x)

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
        """
                All the data sent through this method is sent from client to daemon.
              """

        self._decoder.decode(data)
        self._flush()

    def writeSequence(self, data):
        self._transport.writeSequence(data)

    def getPeer(self):
        return self._transport.getPeer()

    def getHost(self):
        return self._transport.getHost()