import socket
from threading import Thread

from servers.socket_server import SocketServerInt


class ThreadedTcpSocketServer(socket.socket, SocketServerInt):
    clients = []

    def __init__(self, port=8080, bidning='0.0.0.0', buffer_size=1024):
        socket.socket.__init__(self)
        # To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bidning is None:
            bidning = '0.0.0.0'
        if buffer_size is None:
            buffer_size = 1024

        self.bind((bidning, port))
        self.listen(5)
        self.working = True
        self.buffer_size = buffer_size

    def run(self):
        try:
            self.accept_clients()
        except Exception as ex:
            print(ex)
        finally:
            for client in self.clients:
                client.close()
            self.close()

    def accept_clients(self):
        while self.working:
            try:
                (clientsocket, address) = self.accept()
                # Adding client to clients list
                self.clients.append(clientsocket)
                # Client Connected
                self.onopen(clientsocket)
                # Receiving data from client
                Thread(target=self.recieve, args=(clientsocket,)).start()
            except Exception:
                pass

    def stop(self):
        self.working = False
        self.close()

    def recieve(self, client):
        while self.working:
            data = client.recv(self.buffer_size)
            if data == '':
                break
            # Message Received
            self.onmessage(client, data)
        # Removing client from clients list
        self.clients.remove(client)
        # Client Disconnected
        self.onclose(client)
        # Closing connection with client
        client.close()
        # Closing thread

    def broadcast(self, message):
        # Sending message to all clients
        for client in self.clients:
            client.send(message)

    def onopen(self, client):
        pass

    def onmessage(self, client, message):
        pass

    def onclose(self, client):
        pass


if __name__ == "__main__":
    server = ThreadedTcpSocketServer()
    server.run()
