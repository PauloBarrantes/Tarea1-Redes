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
DEFAULT_MASK = 16

MESSAGE_TYPE_UPDATE = 1
MESSAGE_TYPE_ALIVE = 2
MESSAGE_TYPE_I_AM_ALIVE = 3
MESSAGE_TYPE_FLOOD = 4
MESSAGE_TYPE_DATA = 5
MESSAGE_TYPE_COST_CHANGE = 6
MESSAGE_TYPE_CHANGE_DEATH = 7

MESSAGE_TYPE_REQUEST_NEIGHBORS = 10

'''PRIORITYS'''


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

        ## Data Structures
            ## ReachabilityTables - Routing table
        self.reachability_table = ReachabilityTables()

            ## neighbor table
        self.neighbors_table = NeighborsTable()
            ## neighbor bitmap -  We use it to mark neighbors alive or dead
        self.bitmap = bitmap()
            ## messages queue -

        self.priority_queue_messages = PriorityQueue()

        #socket node

        self.socket_node = socket(AF_INET, SOCK_DGRAM)
        self.socket_node.bind((self.ip, self.port))
        #Bitmap lock

        self.bitmapLock = threading.Lock()

        #We request neighborts to central node
        self.request_neighbors()

        print(BColors.WARNING + "Iniciando el listener " + BColors.ENDC)

        #we fill the bitmap with the neighbors
        self.bitmap.setNeighbors(self.neighbors_table.neighbors)


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
        self.threadUpdates.daemon = True
        self.threadUpdates.start()

        # Run our menu.
        self.menu()
    # Request neighbors
    def request_neighbors(self):


        # We create a request message to send a central node
        request_message = bytearray(MESSAGE_TYPE_REQUEST_NEIGHBORS.to_bytes(1, byteorder="big"))
        request_message.extend(self.mask.to_bytes(1, byteorder="big"))

        print(request_message)

        #We send the message to central node
        self.socket_node.sendto(request_message,(str(CENTRAL_IP), CENTRAL_PORT))

        try:
            #We receive the neighbor table
            neighbors_message = self.socket_node.recv(1024)
            # and how many neighbor we have
            decoded_neighbors = decodeNeighbors(neighbors_message)

            for n in range(0, len(decoded_neighbors)):
                self.neighbors_table.save_address(decoded_neighbors[n][0], decoded_neighbors[n][1], decoded_neighbors[n][2], decoded_neighbors[n][3], False)
            self.neighbors_table.print_table()
        except BrokenPipeError:
            print("Se perdió la conexión con el nodo central")

    ## The messages to me, come here
    def listener(self):

        print ("We are listening in ", self.ip, self.port)

        while True:
            ## Wait for a message
            message, client_addr = self.socket_node.recvfrom(1024)


            ## The message type (first 1 byte)

            messageType = int (message[0])

            ## The node that is talking to me
            ip_source = client_addr[0]
            port_source = int (client_addr[1])

            ## We receive a RT from another node
            if messageType ==  MESSAGE_TYPE_UPDATE:

                decoded_RT = decodeRT(message)

                for i in len(0,decoded_RT):
                    self.reachability_table.save_address(decodeRT[i][0], decodeRT[i][1], decodeRT[i][2], decodeRT[i][3], client_addr[0], DEFAULT_MASK, int(client_addr[1]))

            elif messageType == MESSAGE_TYPE_ALIVE:
                print("MESSAGE_TYPE_ALIVE")
                # Recibir ip,mask,port

                # Guardar en tabla de vecinos que está vivo.
                print("Ip: ",ip_source,port_source)
                self.neighbors_table.mark_awake(ip_source,port_source)
                cost = self.neighbors_table.get_cost(ip_source,port_source)
                self.reachability_table.save_address(ip_source,16,port_source,cost,ip_source,16,port_source)
                ## We send a ACK to the source node
                messageACK = bytearray(MESSAGE_TYPE_I_AM_ALIVE.to_bytes(1, byteorder="big"))
                self.socket_node.sendto(messageACK, client_addr)

            ## We receive a ACK of keep alive from one of my neighbors
            elif messageType == MESSAGE_TYPE_I_AM_ALIVE:
                print("ACK de algún agradable vecino, lo pongo la bandera en true")
                self.bitmapLock.acquire()
                alive = self.bitmap.setTrue(ip_source, port_source)
                self.bitmapLock.release()
            ## We receive a message of flood
            elif messageType == MESSAGE_TYPE_FLOOD:
                pass

            ## We receive a message data
            elif messageType == MESSAGE_TYPE_DATA:

                print("Recibimos un mensaje de datos")

                ## We check if is ours
                msg_for_me = check_message(message, self.ip, self.port)

                if msg_for_me:
                    print("Hemos llegado al destino")
                else:
                    print("No somos el destino de este mensaje, hay que pasarlo a alguien")

                    pivots = self.reachability_table.getPivots(ip_str, port_dest)
                    if pivots != None:
                        self.socket_node.sendto(message, pivots)
                    else:
                        print("We lost")
            elif messageType == MESSAGE_TYPE_COST_CHANGE:
                pass
            elif messageType ==  MESSAGE_TYPE_CHANGE_DEATH:
                pass
            else:
                print("gg")

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

                    encoded_RT = encodeRT(key, message, reachability_table)

                    threadSendRT = threading.Thread(target = self.threadSendRT, args=(ip, port, message))
                    threadSendRT.daemon = True
                    threadSendRT.start()

    def threadSendRT(self, ip, port, reachability_table):
        try:
             self.socket_node.sendto(reachability_table,(ip,port))
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
                self.socket_node.sendto(message,(str(ipDest),int(portDest)))

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
        port_destination = int(port)

        mensaje = input("Escriba el mensaje que desea enviar")
        pivots = self.reachability_table.getPivots(ip_destination,port_destination)
        if pivots != None:

            ## Message Type
            data_message = bytearray(MESSAGE_TYPE_DATA.to_bytes(1, byteorder="big"))
            ## Destination IP
            data_message.extend(bytearray(bytes(map(int, (key2[0]).split(".")))))
            ## Destination Port
            data_message.extend((key2[2]).to_bytes(2, byteorder="big"))
            ## Lenght of Data (2 Bytes)
            data_message.extend((key2[2]).to_bytes(2, byteorder="big"))
            ## Message (N Bytes)
            data_message.extend((key2[2]).to_bytes(2, byteorder="big"))

            self.socket_node.sendto(data_message, pivots)
        else:
            print("No hay camino para ese nodo GG")

    def terminate_node(self):
        print("Eliminado el nodo.")

    def changeCost(self):
        # Print our menu.
        print(BColors.WARNING + "Bienvenido al cambio de costo de un enlace: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)


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
            self.changeCost()
            self.menu()
        elif user_input == "2":
            self.sendMessage()
            self.menu()
        elif user_input == "3":
            self.terminate_node()

        elif user_input == "4":
            self.reachability_table.print_table()
            self.neighbors_table.print_table()
            self.menu()
        elif user_input == "5":
            print("Terminando ejecución.")
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.menu()


'''CLASS BITMAP'''
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
#
# port = input("port: ")
# nodoUDP = NodeUDP("127.0.0.1",int(port))
