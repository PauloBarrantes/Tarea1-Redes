import threading
from Node import *
from ReachabilityTables import *
from TablaTCP import *
from socket import *
from texttable import *

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


class NodeTCP(Node):

    def __init__(self, ip, port):
        super().__init__("pseudoBGP", ip, int(port))
        self.ReachabilityTable = ReachabilityTables()
        self.TablaTCP = TablaTCP()
        #Arrancamos el hilo del servidor
        self.threadServer = threading.Thread(target = self.serverTCP)
        self.threadServer.daemon = True
        self.threadServer.start()
        #Acá debemos crear una UI para interactuar con el usuario
        #Recibir los mensajes - n - ip - puerto - máscara - costo
        self.listen()

    def serverTCP(self):
        serverSocket = socket(AF_INET,SOCK_STREAM)
        serverSocket.bind((self.ip,self.port))
        serverSocket.listen(100)
        print ("The server is ready to receive : ", self.ip, self.port)

        while True:
            connectionSocket, addr = serverSocket.accept()
            self.threadServer = threading.Thread(target = self.serverTCPthread, args=(connectionSocket,addr,))
            self.threadServer.daemon = True
            self.threadServer.start()


    def serverTCPthread(self, connectionSocket,addr):
        flag = True
        while flag:
            try:
                mensaje = connectionSocket.recv(1024)
                if int.from_bytes(mensaje, byteorder="big") != 0:
                    cantidad_elementos = int.from_bytes(mensaje[:2], byteorder="big")
                    table = Texttable()
                    table.set_cols_align(["l", "r", "c","k"])
                    table.set_cols_valign(["t", "m", "b","a"])
                    table.add_row(["IP de origen", "Ip", "Máscara","Costo"])
                    for n in range(0,cantidad_elementos):
                        ip_bytes = mensaje[2+(n*8):6+(n*8)]
                        mask = mensaje[6+(n*8)]
                        cost_bytes = mensaje[7+(n*8):10+(n*8)]
                        ip = list(ip_bytes)
                        ip_str = ""
                        for byte in range(0,len(ip)):
                            if(byte < len(ip)-1):
                                ip_str += str(ip[byte])+"."
                            else:
                                ip_str += str(ip[byte])
                        mask_str = str(mask)
                        cost = int.from_bytes(cost_bytes,byteorder="big")
                        #self.imprimirMensaje(addr[0],ip_str,mask_str,cost)
                        table.add_row([addr[0],ip_str,mask_str, cost])
                        self.ReachabilityTable.agregarDireccion(ip_str,addr[0],mask_str,cost)
                    mensajeVuelta = bytes([1])
                    try:
                        connectionSocket.send(mensajeVuelta)
                    except BrokenPipeError:
                        print("Se perdió la conexión")
                        flag = False;
                    print (table.draw() + "\n")
    ### Hay que borrar el nodo que está en la tabla TCP y de la tabla de alcanzabilidad
                else:
                    ip = addr[0]
                    puerto = int(adrr[1])
                    self.TablaTCP.eliminarConexion(addr[0],int(addr[1]))
                    self.ReachabilityTable.eliminarDireccion(addr[0])


            except ConnectionResetError:
                self.TablaTCP.eliminarConexion(addr[0],int(addr[1]))
                print("La conexión se ha perdido con ", addr[0],addr[1])
                flag = False;
        print("Chau Hilo Servidor")
        #connectionSocket.close()



    """Enviar Mensajes a otro nodos"""
    def enviarMensajes(self):
        print("Enviar mensaje:")
        ipDestino = input("Digite la ip de destino a la que desea enviar: ")
        maskDestino = input("Digite la máscara de destino a la que desea enviar: ")
        portDestino = input("Digite el puerto de destino a la que desea enviar: ")

        n = input("Digite la cantidad de mensajes que va enviar a ese destino: ")

        try:
            num = int(n)
        except ValueError:
            print(bcolors.FAIL+ "Error: " + bcolors.ENDC +"Entrada no númerica" )

        portDestino = int(portDestino)
        maskDestino = int(maskDestino)
        cantidad_elementos = (num).to_bytes(2,byteorder="big")
        byte_array = bytearray(cantidad_elementos)
        for i in range(0,num):
            ip1 = input("Digite una dirección ip: ")
            mask1 = input("Digite una máscara: ")
            cost1 = input("Digite un costo: ")
            ip_bytes = bytes(map(int, ip1.split(".")))
            byte_array.extend(bytearray(ip_bytes))
            mask_bytes = (int(mask1)).to_bytes(1,byteorder="big")
            byte_array.extend(mask_bytes)
            cost_bytes = int((cost1)).to_bytes(3,byteorder="big")
            byte_array.extend(cost_bytes)
        try:
            if self.TablaTCP.buscarConexion(ipDestino,portDestino) != -1:
                self.TablaTCP.buscarConexion(ipDestino,portDestino).send(byte_array)
                estado = self.TablaTCP.buscarConexion(ipDestino,portDestino).recv(1024)
                estadoInt = int.from_bytes(estado, byteorder="big")
                if estadoInt == 1:
                    print("Success")
                else:
                    print("Ha ocurrido un error")
            else:
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect((ipDestino,portDestino))
                self.TablaTCP.guardarConexion(ipDestino, portDestino, clientSocket)

                clientSocket.send(byte_array)
                estado = clientSocket.recv(1024)
                estadoInt = int.from_bytes(estado, byteorder="big")
                if estadoInt == 1:
                    print("Success")
                else:
                    print("Ha ocurrido un error")
        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")
        #print ("From Server:" , int.from_bytes(modifiedSentence, byteorder="big"))
        #clientSocket.close()


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
