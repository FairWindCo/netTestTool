from servers.multi_thread_server import ThreadedTcpSocketServer


class EchoServer(ThreadedTcpSocketServer):
    def onmessage(self, client, message):
        client.send(message)


