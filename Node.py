import socket

class Node:
    def __init__(self, protocolo, dirNodo, numeroPuerto):
        self.protocolo = protocolo
        self.direccionNodo = dirNodo
        self.puertoNodo = int(numeroPuerto)

    def __del__(self):
        print("Node was successfully deleted")

    def broadcastClosure():
        #send messages
        pass


