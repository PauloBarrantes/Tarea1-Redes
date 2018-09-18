import socket

class Node:
    def __init__(self, protocolo, dirNodo, numeroPuerto):
        self.protocolo = protocolo
        self.direccionNodo = dirNodo
        self.puertoNodo = int(numeroPuerto)


