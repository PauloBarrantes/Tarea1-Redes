from socket import *
class TCPNode :
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
    def connect(self, host, port):
        self.socket.connect((host, port))
    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
    def port(self, arg):
        pass
