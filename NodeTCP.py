import threading
import Node
from socket import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\33[93m'
    FAIL = '\033[91m'
    GG = '\033[96m'

    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

## Menu

from ReachabilityTables import *

class NodeTCP(Node):

    def __init__(self, ip, port):
        super().__init__("pseudoBGP", ip, int(port))
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
        self.clientSocket =1


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
        print(bcolors.WARNING+"Welcome!, Node: " +self.ip,":",str(self.port) +bcolors.ENDC)
        print(bcolors.OKGREEN+"Instrucciones: "+bcolors.ENDC)
        print(bcolors.BOLD+"-1-"+bcolors.ENDC,"Enviar un mensaje a otro nodo")
        print(bcolors.BOLD+"-2-"+bcolors.ENDC,"Matar a este nodo :(")
        print(bcolors.BOLD+"-3-"+bcolors.ENDC,"Salir")


        entrada = input("Desea enviar un mensaje, borrar al nodo o salir\n")
        print("Usted digito :", entrada)
        if entrada == "1":
            self.enviarMensajes()
            self.listen()
        elif entrada == "2":
            print ("Eliminando nodo")
            self.eliminarNodo()
        else:
            print("salir")


class NodeTCPServidor(threading.Thread):
    """docstring for NodeTCPClient."""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.serverSocket = socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind((self.ip,self.port))
        self.serverSocket.listen(100)

    def run(self):
        print ("The server is ready to receive : ", self.ip, self.port)
        while 1:
            connectionSocket, addr = self.serverSocket.accept()
            sentence = connectionSocket.recv(1024)
            capitalizedSentence = sentence.upper()
            print("Impresión",sentence.upper())
            connectionSocket.send(capitalizedSentence)
            connectionSocket.close()


Node = NodeTCP('localhost',8080)
