import socket
from threading import Thread

from servers.socket_server import SocketServerInt


class ThreadedUdpSocketServer(socket.socket, SocketServerInt):
    clients = []

    def __init__(self, port=8080, bidning='0.0.0.0', max_buffer=1024):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        # To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bidning is None:
            bidning = '0.0.0.0'
        if max_buffer is None:
            max_buffer=1024
        self.bind((bidning, port))
        self.my_max_buffer = max_buffer

    def stop(self):
        self.close()

    def run(self):
        print("Server started")
        try:
            self.accept_clients()
        except Exception as ex:
            print(ex)
        finally:
            print("Server closed")
            for client in self.clients:
                client.close()
            self.close()

    def accept_clients(self):
        while 1:
            data, addr = self.recvfrom(self.my_max_buffer)
            self.onmessage(addr, data)

    def recieve(self, client):
        while 1:
            data = client.recv(1024)
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
        self.sendto(message, client)

    def onclose(self, client):
        pass


if __name__ == "__main__":
    server = ThreadedUdpSocketServer()
    server.run()
