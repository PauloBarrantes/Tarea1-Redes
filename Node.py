import socket

class Node:
    def __init__(self, protocol, ipNode, port):
        self.protocol = protocol
        self.ip = ipNode
        self.port = int(port)

    def __del__(self):
        print("Node was successfully deleted")

    def broadcastClosure():
        #send messages
        pass


