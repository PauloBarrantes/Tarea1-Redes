import socket
class Node :
    """docstring for Node."""
    def __init__(self, addrIP, port):
        self.addrIP = addrIP
        self.port = port
        self.socket = socket.socket()
        self.socket.bind((self.addrIP, self.port))
        self.socket.listen(10)
        print("Node Created: ", addrIP,":",port)
        while True:
            connection, addr = self.socket.accept()
            print("New Connection")
            print(addr)
