import threading
from Node import *
from socket import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    GG = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

## Menu

from ReachabilityTables import *

class NodeTCP(Node):
    def serverTCP(self):
        self.serverSocket = socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind((self.ip,self.port))
        self.serverSocket.listen(100)
        print ("The server is ready to receive : ", self.ip, self.port)
        while True:
            connectionSocket, addr = self.serverSocket.accept()
            mensaje = connectionSocket.recv(1024)
            print("Mensaje: ", mensaje)
            error = bytes([2])
            connectionSocket.send(error)
            connectionSocket.close()
    def __init__(self, ip, port):
        super().__init__("pseudoBGP", ip, int(port))
        self.ReachabilityTable = ReachabilityTables()
        self.ReachabilityTable.agregarDireccion('localhost','localhost','24',2000)
        self.ReachabilityTable.imprimirTabla()
        self.ReachabilityTable.agregarDireccion('localhost','localhost','24',3000)
        self.ReachabilityTable.imprimirTabla()
        self.ReachabilityTable.eliminarDireccion('localhost')
        self.ReachabilityTable.imprimirTabla()
        #Arrancamos el hilo del servidor
        self.threadServer = threading.Thread(target = self.serverTCP)
        ## Esto hace que cuando el hilo principal muera el thread server
        self.threadServer.daemon = True
        self.threadServer.start()
        #Acá debemos crear una UI para interactuar con el usuario
        #Recibir los mensajes - n - ip - puerto - máscara - costo
        self.listen()

    """Enviar Mensajes a otro nodos"""
    def enviarMensajes(self):
        ##Destino yo mismo
        ##n
        ipDestino = "localhost"
        maskDestino = "24"
        portDestino = "8080"
        n = "3"
        ipn1 = "192.16.128.0"
        mask1 = "24"
        cost1 = "1080"

        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((str(self.ip),self.port))
        portDestino = int(portDestino)
        maskDestino = int(maskDestino)
        cantidad_elementos = (int(n)).to_bytes(2,byteorder="big")
        byte_array = bytearray(cantidad_elementos)
        for i in range(0,int(n)):
            ip_bytes = bytes(map(int, ipn1.split(".")))
            byte_array.extend(bytearray(ip_bytes))
            mask_bytes = (int(mask1)).to_bytes(1,byteorder="big")
            byte_array.extend(mask_bytes)
            cost_bytes = int((cost1)).to_bytes(3,byteorder="big")
            byte_array.extend(cost_bytes)
        self.clientSocket.send(byte_array)
        modifiedSentence = self.clientSocket.recv(1024)
        print ("From Server:" , modifiedSentence)
        self.clientSocket.close()


    def eliminarNodo(self):
        print("Matar al Nodo")


    def listen(self):
        print(bcolors.WARNING+"Welcome!, Node: " +self.ip,":",str(self.port) +bcolors.ENDC)
        print(bcolors.OKGREEN+"Instrucciones: "+bcolors.ENDC)
        print(bcolors.BOLD+"-1-"+bcolors.ENDC,"Enviar un mensaje a otro nodo")
        print(bcolors.BOLD+"-2-"+bcolors.ENDC,"Matar a este nodo :(")
        print(bcolors.BOLD+"-3-"+bcolors.ENDC,"Imprimir la tabla de alcanzabilidad")
        print(bcolors.BOLD+"-4-"+bcolors.ENDC,"Salir")


        entrada = input("Qué desea hacer?\n")
        if entrada == "1":
            self.enviarMensajes()
            self.listen()
        elif entrada == "2":
            print ("Eliminando nodo")
            self.eliminarNodo()
        elif entrada == "3":
            self.ReachabilityTable.imprimirTabla()
            self.listen()
        else:
            print("Saliendo")




#Node = NodeTCP('localhost',8081)
