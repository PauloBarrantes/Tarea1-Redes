import threading
from socket import *

exitFlag = 0
import time

from ReachabilityTables import *

class NodeTCP():

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = NodeTCPClient(self.ip, self.port)
        self.server = NodeTCPServidor(self.ip, self.port)
        #self.ReachbilityTable = ReachabilityTables()
        #Arrancamos el hilo del servidor
        self.server.start()
        #Acá debemos crear una UI para interactuar con el usuario
        #Recibir los mensajes - n - ip - puerto - máscara - costo
        self.client.listen()


        self.server.join()

#buscar llamado a super con el protocolo pseudoBGP


class NodeTCPClient():
    """docstring for NodeTCPClient."""
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.clientSocket = 1


    def enviarMensajes(self):
        print("enviarmensaje")
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((str(self.ip),self.port))
        sentence = str.encode(input("Input lowercase sentence:"))
        self.clientSocket.send(sentence)
        modifiedSentence = self.clientSocket.recv(1024)
        print ("From Server:" , modifiedSentence)
        self.clientSocket.close()
    def eliminarNodo(self):
        print("morí")
    def listen(self):
        entrada = input("Desea enviar un mensaje, borrar al nodo o irse a la chingada \n")
        print("Usted digito :", entrada)
        if entrada == "1":
            self.enviarMensajes()
        elif entrada == "2":
            print ("Vayasé al carajo")
        else:
            self.eliminarNodo()


class NodeTCPServidor(threading.Thread):
    """docstring for NodeTCPClient."""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        print("GG", ip, port)
        self.serverSocket = socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind((self.ip,self.port))
        self.serverSocket.listen(100)

    def run(self):
        print ("The server is ready to receive : ", self.ip, self.port)
        while 1:
            connectionSocket, addr = self.serverSocket.accept()
            sentence = connectionSocket.recv(1024)
            capitalizedSentence = sentence.upper()
            print("IMPRESI´ON DEL SERVIDOR",sentence.upper())
            connectionSocket.send(capitalizedSentence)
            connectionSocket.close()


Node = NodeTCP('localhost',8080)
