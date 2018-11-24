from Node import *
from socket import *
from NeighborsTable import *
from ReachabilityTables import *
from encoder_decoder import *
from queue import PriorityQueue
import time


'''TIMEOUTS'''

TIMEOUT_UPDATES  = 30
TIMEOUT_ACK = 2
TIMEOUT_ALIVE_MESSAGES = 120

'''CONSTANTS'''

MESSAGE_TYPE_UPDATE = 1
MESSAGE_TYPE_ALIVE = 2
MESSAGE_TYPE_I_AM_ALIVE = 3
MESSAGE_TYPE_FLOOD = 4
MESSAGE_TYPE_DATA = 5
MESSAGE_TYPE_COST_CHANGE = 6
MESSAGE_TYPE_CHANGE_DEATH = 7

MESSAGE_TYPE_REQUEST_NEIGHBORS = 10

'''CENTRAL NODE'''

CENTRAL_IP = "127.0.0.1"
CENTRAL_MASK = 16
CENTRAL_PORT = 9000


'''TERMINAL COLORS'''

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    GG = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class NodeUDP(Node):

    def __init__(self, ip, port):
        super().__init__("intAS", ip, int(port))

        self.reachability_table = ReachabilityTables()
        self.neighbors_table = NeighborsTable()
        self.bitmap = bitmap()
        self.node_socket = socket(AF_INET, SOCK_DGRAM)
        self.node_socket.bind((self.ip, self.port))

        self.bitmapLock = threading.Lock()
        # Continue the server, even after our main thread dies.


        #We request neighborts to central node
        self.request_neighbors()

        print(BColors.WARNING + "Iniciando el listener " + BColors.ENDC)
        self.bitmap.setNeighbors(self.neighbors_table.neighbors)


        print("BITMAP: ",self.bitmap.bitmap)
        # Start listener thread.
        self.threadListener = threading.Thread(target = self.listener)
        self.threadListener.daemon = True
        self.threadListener.start()
        # We start threadAliveMessage
        print(BColors.WARNING + "Iniciando el hilo que busca vida" + BColors.ENDC)
        self.principalThreadAliveMessage = threading.Thread(target = self.aliveMessages)
        self.principalThreadAliveMessage.daemon = True
        self.principalThreadAliveMessage.start()

        time.sleep(2)
        print(BColors.WARNING + "Iniciando el hilo que esta enviando updates" + BColors.ENDC)

        self.threadUpdates = threading.Thread(target = self.sendRT)
        # Continue the server, even after our main thread dies.
        self.threadUpdates.daemon = True
        self.threadUpdates.start()

        # Run our menu.
        self.menu()
    # Request neighbors
    def request_neighbors(self):

        request_message = bytearray(MESSAGE_TYPE_REQUEST_NEIGHBORS.to_bytes(1, byteorder="big"))
        request_message.extend(self.mask.to_bytes(1, byteorder="big"))



        self.node_socket.sendto(request_message,(str(CENTRAL_IP), CENTRAL_PORT))

        try:
            neighbors_message = self.node_socket.recv(1024)
            elements_quantity = int.from_bytes(neighbors_message[:2], byteorder="big")

            '''RECORDAR SACAR DE ACA - FLA'''
            for n in range(0, elements_quantity):
                ip_bytes = neighbors_message[2+(n*10):6+(n*10)]

                mask = neighbors_message[6+(n*10)]
                port_bytes = neighbors_message[7+(n*10):9+(n*10)]
                cost_bytes = neighbors_message[9+(n*10):12+(n*10)]
                ip = list(ip_bytes)
                ip_str = ""
                for byte in range(0,len(ip)):
                    if(byte < len(ip)-1):
                        ip_str += str(ip[byte])+"."
                    else:
                        ip_str += str(ip[byte])

                port = int.from_bytes(port_bytes, byteorder="big")
                cost = int.from_bytes(cost_bytes, byteorder="big")
                self.neighbors_table.save_address(ip_str, mask, port, cost, False)
            self.neighbors_table.print_table()
        except BrokenPipeError:
            print("Se perdió la conexión con el nodo central")


    def listener(self):

        print ("We are listening in ", self.ip, self.port)
        priority_queue = PriorityQueue()
        while True:
            message, client_addr = self.node_socket.recvfrom(1024)

            messageType = int (message[0])


            ip_source = client_addr[0]

            port_source = int (client_addr[1])


            if messageType ==  MESSAGE_TYPE_UPDATE:
                print("Recibimos un mensaje de actualización de : " ,ip_source, port_source)

                self.updateRT(message)
            elif messageType == MESSAGE_TYPE_ALIVE:
                print("MESSAGE_TYPE_ALIVE")
                # Recibir ip,mask,port

                # Guardar en tabla de vecinos que está vivo.
                print("Ip: ",ip_source,port_source)
                self.neighbors_table.mark_awake(ip_source,port_source)
                cost = self.neighbors_table.get_cost(ip_source,port_source)
                self.reachability_table.save_address(ip_source,16,port_source,cost,ip_source,16,port_source)

                message = bytearray(MESSAGE_TYPE_I_AM_ALIVE.to_bytes(1, byteorder="big"))

                self.node_socket.sendto(message, client_addr)


            elif messageType == MESSAGE_TYPE_I_AM_ALIVE:
                print("ACK de algún agradable vecino, lo pongo la bandera en true")
                self.bitmapLock.acquire()
                alive = self.bitmap.setTrue(ip_source, port_source)
                self.bitmapLock.release()
            elif messageType == MESSAGE_TYPE_FLOOD:
                pass
            elif messageType == MESSAGE_TYPE_DATA:
                pass
            elif messageType == MESSAGE_TYPE_COST_CHANGE:
                pass
            elif messageType ==  MESSAGE_TYPE_CHANGE_DEATH:
                pass
            else:
                print("gg")

    def updateRT(self, messageRT):
        elements_quantity = int.from_bytes(messageRT[1:3], byteorder="big")
        for n in range(0, elements_quantity):
            ip_bytes = messageRT[3+(n*10):7+(n*10)]
            mask = messageRT[7+(n*10)]
            port_bytes = messageRT[8+(n*10):10+(n*10)]
            cost_bytes = messageRT[10+(n*10):13+(n*10)]
            ip = list(ip_bytes)
            ip_str = ""
            for byte in range(0,len(ip)):
                if(byte < len(ip)-1):
                    ip_str += str(ip[byte])+"."
                else:
                    ip_str += str(ip[byte])
            port = int.from_bytes(port_bytes, byteorder="big")
            cost = int.from_bytes(cost_bytes, byteorder="big")
            print(ipstr,"-",mask,"-",port,"-",cost)
            self.reachability_table.save_address(ip_str, mask, port, cost, client_addr[0], mask, int(client_addr[1]))
    def sendRT(self):
        while True:
            time.sleep(TIMEOUT_UPDATES)
            print("Enviando Actualización")
            for key in list(self.neighbors_table.neighbors):
                if self.neighbors_table.is_awake(key[0],key[1]) == 1:
                    ip = key[0]
                    port = key[1]
                    cost = self.neighbors_table.neighbors.get(key)[0]

                    message = bytearray(MESSAGE_TYPE_UPDATE.to_bytes(1, byteorder="big"))
                    reach_counter = 0
                    for key2 in list(self.reachability_table.reach_table):
                        if key2 != key:
                            reach_counter += 1
                            message.extend(bytearray(bytes(map(int, (key2[0]).split(".")))))
                            message.extend(key2[1].to_bytes(1, byteorder="big"))
                            message.extend((key2[2]).to_bytes(2, byteorder="big"))
                            message.extend(self.reachability_table.reach_table.get(key2)[0]).to_bytes(3, byteorder="big")

                    message[1:3] = reach_counter.to_bytes(2, byteorder="big")

                    threadSendRT = threading.Thread(target = self.threadSendRT, args=(ip, port, message))
                    threadSendRT.daemon = True
                    threadSendRT.start()

    def threadSendRT(self, ip, port, reachability_table):
        try:
             self.node_socket.sendto(reachability_table,(ip,port))
        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")
            self.neighbors_table.mark_dead(ipDest, portDest)






    # Send messages to another node.
    def aliveMessages(self):
        message = bytearray(MESSAGE_TYPE_ALIVE.to_bytes(1, byteorder="big"))

        while True:
            for key in list(self.neighbors_table.neighbors):
                ipNeighbor = key[0]
                portNeighbor = key[1]
                cost = self.neighbors_table.get_cost(ipNeighbor,portNeighbor)

                # Thread send alive messages to specific neighbor
                threadAliveMessageToNeighbor = threading.Thread(target = self.threadAliveMessage, args=(ipNeighbor, portNeighbor, cost,message))
                threadAliveMessageToNeighbor.daemon = True
                threadAliveMessageToNeighbor.start()
            time.sleep(TIMEOUT_ALIVE_MESSAGES)

    # Thread manda mensajes a cada vecino y espera el ACK

    def threadAliveMessage(self, ipDest, portDest, cost,message):
        attempts = 0
        self.bitmapLock.acquire()
        alive = self.bitmap.getBit(ipDest, portDest)
        self.bitmapLock.release()
        while attempts < 3 and not alive:
            try:
                print("Enviando a Nodo ", ipDest , "-" , portDest, "intento: " , attempts)
                self.node_socket.sendto(message,(str(ipDest),int(portDest)))

            except BrokenPipeError:
                print("Se perdió la conexión con el servidor")
            time.sleep(5)
            self.bitmapLock.acquire()
            alive = self.bitmap.getBit(ipDest, portDest)
            self.bitmapLock.release()

            attempts += 1
        print("Cantidad de attempts", attempts)


        ## We need to compare states between neighbortable and bitmap
        awakeNeighbor = self.neighbors_table.is_awake(ipDest,portDest)
        ## My neighbor has died and I do not notice
        print(ipDest , "-" , portDest,"Node awakener: ", awakeNeighbor ,"Bandera: " , alive)
        if awakeNeighbor and not alive:
            ## We need to make a flush
            self.neighbors_table.mark_dead(ipDest,portDest)

            print("Acá hicimos una inundación")


        elif not awakeNeighbor and alive:
            self.neighbors_table.mark_awake(ipDest,portDest)
            self.reachability_table.save_address(ipDest,16,portDest,cost,ipDest,16,portDest)

        else:
            print("Estaba muerto y sigue muerto o  estaba vivo y sigue vivo")



    def sendMessage(self):
        self.log_writer.write_log("UDP node is sending a message.", 2)

        # Variables that we will use to keep the user's input.
        port = ""
        ip_destination = ""
        mensaje = ""
        # Variable to check each input of the user.
        valid_input = False
        while not valid_input:
            ip_destination = input("Digite la ip de destino a la que desea enviar: ")
            valid_input = self.validate_ip(ip_destination)

        valid_input = False
        while not valid_input:
            port = input("Digite el puerto de destino a la que desea enviar: ")
            valid_input = self.validate_port(port)

        mensaje = input("Escriba el mensaje que desea enviar")


        port_destination = int(port)

    def terminate_node(self):
        print("Eliminado el nodo.")

    def menu(self):

        # Print our menu.
        print(BColors.WARNING + "Bienvenido!, Al Nodo: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Cambiar el costo de enlace con un nodo")
        print(BColors.BOLD + "-2-" + BColors.ENDC, "Enviar un mensaje a un nodo")
        print(BColors.BOLD + "-3-" + BColors.ENDC, "Terminar a este nodo")
        print(BColors.BOLD + "-4-" + BColors.ENDC, "Imprimir la tabla de enrutamiento vigente")
        print(BColors.BOLD + "-5-" + BColors.ENDC, "Salir")

        user_input = input("Qué desea hacer?\n")
        if user_input == "1":
            print("Cambiando el costo de un enlace")

            self.menu()
        elif user_input == "2":
            print("Enviando mensaje")
        elif user_input == "3":
            print ("Eliminando nodo - need a fix")

            self.menu()
        elif user_input == "4":
            self.reachability_table.print_table()
            self.neighbors_table.print_table()
            self.menu()
        elif user_input == "5":
            print("Terminando ejecución.")
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.menu()
class bitmap():
    """docstring for ."""
    def __init__(self):
        self.bitmap = {}

    def setNeighbors(self,neighbors):
        for key in list(neighbors):
            self.bitmap[(key[0],key[1])] = False

    def getBit(self, ip, port):
        return self.bitmap[(ip,port)]

    def setFalse(self):
        for key in list(self.bitmap):
            self.bitmap[(key[0],key[1])] = False
    def setTrue(self, ip, port):
        self.bitmap[(ip,port)] = True

port = input("port: ")
nodoUDP = NodeUDP("127.0.0.1",int(port))
