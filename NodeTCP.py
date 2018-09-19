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
    def __init__(self, ip, port):
        super().__init__("pseudoBGP", ip, int(port))
        self.serverSocket = 0
        self.flag = True
        self.ReachabilityTable = ReachabilityTables()
        #Arrancamos el hilo del servidor
        self.hilo = threading.Thread(target = self.server)
        self.hilo.daemon = True
        self.hilo.start()
        #Acá debemos crear una UI para interactuar con el usuario
        #Recibir los mensajes - n - ip - puerto - máscara - costo
        self.listen()

    def server(self):
        self.ReachabilityTable.imprimirTabla()

        self.serverSocket = socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind((self.ip,self.port))
        self.serverSocket.listen(100)
        print ("The server is ready to receive : ", self.ip, self.port)
        while self.flag:
            connectionSocket, addr = self.serverSocket.accept()
            print(addr[0])
            mensaje = connectionSocket.recv(1024)
            cantidad_elementos = int.from_bytes(mensaje[:2], byteorder="big")
            for n in range(0,cantidad_elementos):
                ip_bytes = mensaje[2:6]
                mask_bytes = mensaje[7]
                cost_bytes = mensaje[8:]
                ip = list(ip_bytes)
                ip_str = ""
                for byte in ip:
                    if(byte < len(ip)):
                        ip_str += str(ip[byte])+"."
                    else:
                        ip_str += str(ip[byte])
                mask_str = str(int.from_bytes(mask_bytes,byteorder="big"))
                cost = int.from_bytes(cost_bytes,byteorder="big")
                print(addr[0],ip_str,mask_str,cost)
                self.ReachabilityTable.agregarDireccion(addr[0],ip_str,mask_str,cost)
            print("Mensaje: ", mensaje)
            error = bytes([2])
            connectionSocket.send(error)
            connectionSocket.close()

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
        print ("From Server:" , int.from_bytes(modifiedSentence, byteorder="big"))
        self.clientSocket.close()


    def eliminarNodo(self):
        print("Morí T.T")


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
            print ("Imprimiendo tablita")
        else:
            print("salir")




Node = NodeTCP('localhost',8081)
