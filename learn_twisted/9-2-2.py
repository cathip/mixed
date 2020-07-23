from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor


class SpreadFactoty(Factory):

    def __init__(self):
        self.numPortocols = 0

    def buildProtocol(self, addr):
        return Spreader(self)

endpoint = TCP4ClientEndpoint(reactor, 8007)
endpoint.listen(SpreadFactoty())
reactor.run()