from twisted.internet.interfaces import IProcessProtocol, ITransport, IConsumer, IProcessTransport
from twisted.internet.protocol import ProcessProtocol
from zope.interface.declarations import implements

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

class _AuthorizedTransportWrapper(object):
    implements(IProcessTransport)

    def __init__(self, transport):
        assert IProcessTransport.providedBy(transport)

        self.transport = transport
        self.data = []

    def closeStdin(self):
        self.transport.closeStdin()

    def closeStdout(self):
        self.transport.closeStdout()

    def closeChildFD(self, descriptor):
        self.transport.closeChildFD(descriptor)

    def writeToChild(self, childFd, data):
        self.transport.writeToChild(childFd, data)

    def loseConnection(self):
        self.transport.loseConnection()

    def signalProcess(self, signalID):
        self.transport.signalProcess(signalID)

    def write(self, data):
        print "RAW (sent): ", data

        # Capture pushes by client
        self.data.append(data)

        if data[-4:] == "0000":
            print "SENT (by client): ", _decodeGitList(''.join(self.data))
            self.transport.write(''.join(self.data))

            self.data = []

    def writeSequence(self, data):
        self.transport.writeSequence(data)

    def getPeer(self):
        return self.transport.getPeer()

    def getHost(self):
        return self.transport.getHost()

class AuthorizedProcessProtocolWrapper(object):
    implements(IProcessProtocol)
    
    def __init__(self, proto):
        assert isinstance(proto, ProcessProtocol)
        
        self.proto = proto
        self.data = []
        
    def makeConnection(self, process):
        self.proto.makeConnection(_AuthorizedTransportWrapper(process))
        
    def childDataReceived(self, childFD, data):
        print "RAW (received): ",data

        if (data[:2] == "00"):
            self.data.append(data)

            if data[-4:] == "0000":
                print "RECEIVED (by client): ", _decodeGitList(''.join(self.data))
                self.proto.childDataReceived(childFD, ''.join(self.data))

                self.data = []
        else:
            self.proto.childDataReceived(childFD, data)
        
    def childConnectionLost(self, childFD):
        self.proto.childConnectionLost(childFD)
        
    def processExited(self, reason):
        self.proto.processExited(reason)

    def processEnded(self, reason):
        self.proto.processEnded(reason)