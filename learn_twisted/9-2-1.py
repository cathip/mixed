from twisted.internet.protocol import Protocol

clients = []

class Spreader(Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.transport.write(
            (u"欢迎来到Spread Site, 您是第%d个客户端用户！\n" %
            (self.factory.numProtocols,).encode('utf8'))
        )
        print("new connect: %d" % self.factory.numProtocols)
        clients.append(self)

    def connectionLost(self, reason):
        clients.remove(self)
        print("lost connect: %s" % self.connect_id)

    def dataReceived(self, data):
        if data == "close":
            self.transport.loseConnection()
            print("%s closed" % self.connect_id)
        else:
            print("spreading message form %s : %s" % (self.connect_id, data))
            for client in clients:
                if client != self:
                    client.transport.write(data)
