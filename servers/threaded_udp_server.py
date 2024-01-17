import socket
import time
from threading import Thread

from servers.socket_server import SocketServerInt


class ThreadedUdpSocketServer(socket.socket, SocketServerInt):
    clients = []

    def __init__(self, port=8080, bidning='0.0.0.0', max_buffer=1024):
        # print("create server socket")
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        # To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bidning is None:
            bidning = '0.0.0.0'
        if max_buffer is None:
            max_buffer = 1024
        try:
            self.bind((bidning, port))
            self.my_max_buffer = max_buffer
            self.working = True
        except OSError as error:
            print(bidning, port, error)
            self.working = False

    def stop(self):
        if self.working:
            self.working = False
            self.close()
            print("Server stopped")

    def run(self):
        # print("UDP Server started")
        try:
            self.accept_clients()
        except Exception as ex:
            print("UDP: Server:", ex)
        finally:
            # print("UDP Server closed")
            self.close()
        # print("UDP server shutdown")

    def accept_clients(self):
        while self.working:
            try:
                data, addr = self.recvfrom(self.my_max_buffer)
                self.onmessage(addr, data)
                time.sleep(1)
            except OSError as os:
                if os.errno != 10038:
                    raise os
                else:
                    print("non socket error")

    def onmessage(self, client, message):
        self.sendto(message, client)


if __name__ == "__main__":
    server = ThreadedUdpSocketServer()
    t = Thread(target=server.run)
    # server.run()
    t.start()
    t.join()
