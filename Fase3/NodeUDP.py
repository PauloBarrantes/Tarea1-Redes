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
TIMEOUT_ALIVE_MESSAGES = 90

'''CONSTANTS'''
DEFAULT_MASK = 24

MESSAGE_TYPE_UPDATE = 1
MESSAGE_TYPE_ALIVE = 2
MESSAGE_TYPE_I_AM_ALIVE = 3
MESSAGE_TYPE_FLOOD = 4
MESSAGE_TYPE_DATA = 5
MESSAGE_TYPE_COST_CHANGE = 6
MESSAGE_TYPE_CHANGE_DEATH = 7
MESSAGE_TYPE_REQUEST_NEIGHBORS = 10


AWAKE = 1
IS_NEIGHBOR = True



'''PRIORITYS'''
HIGH_PRIORITY   = 1
NORMAL_PRIORITY = 2
LOW_PRIORITY    = 3

'''CHANGE_COST CONSTANTS'''

ERROR = -1
LOWER_COST = 2
MAJOR_COST = 1
'''CENTRAL NODE'''

CENTRAL_IP = "169.254.65.157"
CENTRAL_MASK = 16
CENTRAL_PORT = 9000

'''# HOPS'''
N_HOPS = 6

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

        self.log_writer = LogWriter(self.ip, self.port)

        #socket node

        self.socket_node = socket(AF_INET, SOCK_DGRAM)
        self.socket_node.bind((self.ip, self.port))
        #Bitmap lock

        self.bitmap_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        self.flag_request_neighbors = False
        self.flag_flush = False

        #We request neighborts to central node
        self.request_neighbors()

        # print(BColors.WARNING + "Iniciando el listener " + BColors.ENDC)

        #we fill the bitmap with the neighbors
        self.bitmap.setNeighbors(self.neighbors_table.neighbors)


        # Start listener thread.
        self.thread_listener = threading.Thread(target = self.listener)
        self.thread_listener.daemon = True
        self.thread_listener.start()


        # Start message processor thread.
        self.thread_message_processor = threading.Thread(target = self.processor_messages)
        self.thread_message_processor.daemon = True
        self.thread_message_processor.start()


        # We start threadAliveMessage
        self.principal_thread_alive_message = threading.Thread(target = self.alive_messages)
        self.principal_thread_alive_message.daemon = True
        self.principal_thread_alive_message.start()


        ## We start the thread of updates
        self.thread_updates = threading.Thread(target = self.send_RT)
        self.thread_updates.daemon = True
        self.thread_updates.start()

        # Run our menu.
        self.menu()
    # Request neighbors
    def request_neighbors(self):


        # We create a request message to send a central node
        request_message = bytearray(MESSAGE_TYPE_REQUEST_NEIGHBORS.to_bytes(1, byteorder="big"))

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
            message, neighbor = self.socket_node.recvfrom(1024)
            messageType = int (message[0])

            ## We assign the prioritys of each message

            if messageType ==  MESSAGE_TYPE_UPDATE:
                priority = LOW_PRIORITY

            elif messageType == MESSAGE_TYPE_ALIVE:
                priority = LOW_PRIORITY

            elif messageType == MESSAGE_TYPE_I_AM_ALIVE:
                priority = LOW_PRIORITY

            elif messageType == MESSAGE_TYPE_FLOOD:
                print("UFALE!")
                priority = HIGH_PRIORITY

            elif messageType == MESSAGE_TYPE_DATA:
                priority = LOW_PRIORITY

            elif messageType == MESSAGE_TYPE_COST_CHANGE:
                priority = NORMAL_PRIORITY

            elif messageType ==  MESSAGE_TYPE_CHANGE_DEATH:
                priority = NORMAL_PRIORITY
            else:
                priority = -1


            if priority != -1:
                self.queue_lock.acquire()
                self.priority_queue_messages.put((priority,message,neighbor))
                self.queue_lock.release()
            else:
                print("Tipo de mensaje inválido")

    def processor_messages(self):
        print ("We are processing messages ")
        while True:
            tuple_message_neighbor = self.priority_queue_messages.get(block=True, timeout=None)

            message = tuple_message_neighbor[1]
            neighbor = tuple_message_neighbor[2]

            ## The message type (first 1 byte)

            messageType = int (message[0])

            ## The node that is talking to me
            ip_source = neighbor[0]
            port_source = int (neighbor[1])

            ## We receive a RT from another node
            if messageType ==  MESSAGE_TYPE_UPDATE:

                decoded_RT = decodeRT(message)
                for i in range(0,len(decoded_RT)):
                    update_cost = self.neighbors_table.get_cost(ip_source, port_source) + decoded_RT[i][3]
                    self.reachability_table.save_address(decoded_RT[i][0], decoded_RT[i][1], decoded_RT[i][2], update_cost, ip_source, DEFAULT_MASK, port_source)

            elif messageType == MESSAGE_TYPE_ALIVE:
                # Recibir ip,mask,port

                # Guardar en tabla de vecinos que está vivo.
                self.neighbors_table.mark_awake(ip_source,port_source)
                self.bitmap_lock.acquire()
                alive = self.bitmap.setTrue(ip_source, port_source)
                self.bitmap_lock.release()
                cost = self.neighbors_table.get_cost(ip_source,port_source)

                self.reachability_table.save_address(ip_source,DEFAULT_MASK,port_source,cost,ip_source,DEFAULT_MASK,port_source)
                ## We send a ACK to the source node
                messageACK = bytearray(MESSAGE_TYPE_I_AM_ALIVE.to_bytes(1, byteorder="big"))
                self.socket_node.sendto(messageACK, neighbor)

            ## We receive a ACK of keep alive from one of my neighbors
            elif messageType == MESSAGE_TYPE_I_AM_ALIVE:
                self.bitmap_lock.acquire()
                alive = self.bitmap.setTrue(ip_source, port_source)
                self.bitmap_lock.release()
            ## We receive a message of flood
            elif messageType == MESSAGE_TYPE_FLOOD:

                hops = int(message[1])



                if hops != 0:
                    hops = hops - 1
                    self.flush(hops)
                else:
                    self.flag_flush = True
            ## We receive a message data
            elif messageType == MESSAGE_TYPE_DATA:
                ## We check if is ours
                msg_for_me = check_message(message, self.ip, self.port)
                elements_quantity = int.from_bytes(message[13:15], byteorder="big")
                message_data = message[15:15+elements_quantity]
                message_data_str = message_data.decode("utf-8")
                if msg_for_me[0]:
                    print("Hemos llegado al destino")
                    print("Mensaje: ",message_data_str)
                else:
                    print("No somos el destino de este mensaje, hay que pasarlo a alguien")
                    print("Mensaje: ",message_data_str)
                    pivots = self.reachability_table.get_pivots(msg_for_me[1], msg_for_me[2])
                    print("Vamos a pasar por: ", pivots)
                    if pivots != None:
                        self.socket_node.sendto(message, pivots)
                    else:
                        print("We lost")
            elif messageType == MESSAGE_TYPE_COST_CHANGE:
                new_cost = int.from_bytes(message[1:4], byteorder="big")
                print("Costo de enlance nuevo:" , new_cost )


                result = self.neighbors_table.change_cost(ip_source, port_source, new_cost)
                if result != ERROR:
                    result_rt = self.reachability_table.change_cost(ip_source, port_source, new_cost)
                    if result_rt != ERROR:

                        if result == MAJOR_COST and result_rt == MAJOR_COST:
                            self.flush(N_HOPS)
                        elif result == LOWER_COST and result_rt == LOWER_COST:
                            print("El costo es menor, eventualmente se va propagar")



            elif messageType ==  MESSAGE_TYPE_CHANGE_DEATH:
                ## We need to make a flush
                self.neighbors_table.mark_dead(ip_source,port_source)
                print(BColors.FAIL + "Se va morir el nodo " + ip_source+ ":"+ str(port_source) + BColors.ENDC)
                self.flush(N_HOPS)
            else:
                print("gg")

    def send_RT(self):
        while True:
            time.sleep(TIMEOUT_UPDATES)
            #print(BColors.WARNING + "Iniciamos un UPDATE" + BColors.ENDC)
            if self.flag_flush == True:
                self.fill_rt()
                self.flag_flush = False


            self.log_writer.write_log("Iniciamos los updates", 1)

            for key in list(self.neighbors_table.neighbors):
                if self.neighbors_table.is_awake(key[0],key[1]) == AWAKE:
                    ip = key[0]
                    port = key[1]
                    cost = self.neighbors_table.neighbors.get(key)[0]

                    message = bytearray(MESSAGE_TYPE_UPDATE.to_bytes(1, byteorder="big"))
                    encodeRT(key, message, self.reachability_table)

                    thread_send_RT = threading.Thread(target = self.thread_send_RT, args=(ip, port, message))
                    thread_send_RT.daemon = True
                    thread_send_RT.start()

    def thread_send_RT(self, ip, port, reachability_table):
        self.log_writer.write_log("Enviamos updates al Nodo (" +ip+","+str(port)+")", 1)

        try:
             self.socket_node.sendto(reachability_table,(ip,port))
        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")
            self.neighbors_table.mark_dead(ipDest, portDest)
    def fill_rt(self):
        for key in list(self.neighbors_table.neighbors):
            if self.neighbors_table.is_awake(key[0],key[1]) == AWAKE:
                ip_neighbor = key[0]
                port_neighbor = key[1]
                cost = self.neighbors_table.get_cost(ip_neighbor,port_neighbor)

                self.reachability_table.save_address(ip_neighbor,DEFAULT_MASK,port_neighbor,cost,ip_neighbor,DEFAULT_MASK,port_neighbor)


    # Send messages to another node.
    def alive_messages(self):
        message = bytearray(MESSAGE_TYPE_ALIVE.to_bytes(1, byteorder="big"))

        while True:
            print(BColors.WARNING + "Iniciamos el Keep Alive" + BColors.ENDC)
            self.bitmap_lock.acquire()
            print("Ponemos el false")
            self.bitmap.set_false()
            self.bitmap_lock.release()
            for key in list(self.neighbors_table.neighbors):
                ip_neighbor = key[0]
                port_neighbor = key[1]
                cost = self.neighbors_table.get_cost(ip_neighbor,port_neighbor)

                # Thread send alive messages to specific neighbor
                thread_alive_message_to_neighbor = threading.Thread(target = self.thread_alive_message, args=(ip_neighbor, port_neighbor, cost,message))
                thread_alive_message_to_neighbor.daemon = True
                thread_alive_message_to_neighbor.start()
            time.sleep(TIMEOUT_ALIVE_MESSAGES)

    # Thread manda mensajes a cada vecino y espera el ACK

    def thread_alive_message(self, ipDest, portDest, cost,message):
        self.log_writer.write_log("Iniciamos el keep alive con (" +ipDest+","+str(portDest)+")", 2)

        attempts = 0
        self.bitmap_lock.acquire()
        alive = self.bitmap.getBit(ipDest, portDest)
        self.bitmap_lock.release()
        while attempts < 3 and not alive:
            try:
                self.socket_node.sendto(message,(str(ipDest),int(portDest)))

            except BrokenPipeError:
                print("Se perdió la conexión con el servidor")
            time.sleep(5)
            self.bitmap_lock.acquire()
            alive = self.bitmap.getBit(ipDest, portDest)
            self.bitmap_lock.release()

            attempts += 1


        ## We need to compare states between neighbortable and bitmap
        awakeNeighbor = self.neighbors_table.is_awake(ipDest,portDest)
        ## My neighbor has died and I do not notice
        if awakeNeighbor and not alive:
            ## We need to make a flush
            self.neighbors_table.mark_dead(ipDest,portDest)
            print(BColors.FAIL + "Murió el nodo " + ipDest+ ":"+ str(portDest) + BColors.ENDC)
            self.log_writer.write_log("El nodo(" +ipDest+","+str(portDest)+") estaba despierto, pero ha muerto", 2)

            self.flush(N_HOPS)

        elif not awakeNeighbor and alive:
            print("Desperto")
            self.log_writer.write_log("El nodo(" +ipDest+","+str(portDest)+") estaba dormido, pero ha despertado", 2)

            self.neighbors_table.mark_awake(ipDest,portDest)
            self.reachability_table.save_address(ipDest,DEFAULT_MASK,portDest,cost,ipDest,DEFAULT_MASK,portDest)
        # elif awakeNeighbor and alive:
        #     self.reachability_table.save_address(ipDest,DEFAULT_MASK,portDest,cost,ipDest,DEFAULT_MASK,portDest)

    #We are going to make a flood to our neighbors
    def flush(self, hops):

        #Delete other messages
        self.queue_lock.acquire()
        self.priority_queue_messages.empty()
        self.queue_lock.release()
        #Delete RT
        self.reachability_table.clear()
        for key in list(self.neighbors_table.neighbors):
            if self.neighbors_table.is_awake(key[0],key[1]) == AWAKE:
                ip = key[0]
                port = key[1]
                message = bytearray(MESSAGE_TYPE_FLOOD.to_bytes(1, byteorder="big"))
                message.extend(hops.to_bytes(1, byteorder="big"))
                self.socket_node.sendto(message,(str(ip),int(port)))


    def send_message(self):
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

        mensaje = input("Escriba el mensaje que desea enviar:")
        pivots = self.reachability_table.get_pivots(ip_destination,port_destination)
        if pivots != None:
            print(pivots)
            ## Message Type
            data_message = bytearray(MESSAGE_TYPE_DATA.to_bytes(1, byteorder="big"))
            ## Source IP
            data_message.extend(bytearray(bytes(map(int, self.ip.split(".")))))
            ## Source Port
            data_message.extend(self.port.to_bytes(2, byteorder="big"))
            ## Destination IP
            data_message.extend(bytearray(bytes(map(int, ip_destination.split(".")))))
            ## Destination Port
            data_message.extend(port_destination.to_bytes(2, byteorder="big"))
            ## Lenght of Data (2 Bytes)
            data_message.extend(len(mensaje).to_bytes(2, byteorder="big"))
            ## Message (N Bytes)
            data_message.extend(mensaje.encode("utf-8"))
            print("ADIOS")
            self.socket_node.sendto(data_message, pivots)
        else:
            print("No hay camino para ese nodo GG")

    def terminate_node(self):
        for key in list(self.neighbors_table.neighbors):
            if self.neighbors_table.is_awake(key[0],key[1]) == AWAKE:
                ip = key[0]
                port = key[1]
                message = bytearray(MESSAGE_TYPE_CHANGE_DEATH.to_bytes(1, byteorder="big"))
                self.socket_node.sendto(message,(str(ip),int(port)))

        time.sleep(6)

    def change_cost(self):
        # Print our menu.
        print(BColors.WARNING + "Bienvenido al cambio de costo de un enlace: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC + "Digite el nodo que al que le vamos a cambiar el costo")
        port = ""
        ip_destination = ""
        new_cost = ""
        # Variable to check each input of the user.
        print("")
        valid_input = False
        while not valid_input:
            ip_destination = input("Digite el ip: ")
            valid_input = self.validate_ip(ip_destination)

        valid_input = False
        while not valid_input:
            port = input("Digite el puerto: ")
            valid_input = self.validate_port(port)
        port_destination = int(port)

        valid_input = False
        while not valid_input:
            new_cost = input("Digite el nuevo costo: ")
            valid_input = self.validate_cost(new_cost)
        new_cost = int(new_cost)

        change_cost_message = bytearray(MESSAGE_TYPE_COST_CHANGE.to_bytes(1, byteorder="big"))
        change_cost_message.extend(new_cost.to_bytes(3, byteorder="big"))

        result_neighbor = self.neighbors_table.change_cost(ip_destination, port_destination, new_cost)
        result_rt = self.reachability_table.change_cost(ip_destination, port_destination, new_cost)
        if result_neighbor != ERROR and result_rt != ERROR:
            self.socket_node.sendto(change_cost_message,(ip_destination,port_destination))
        else:
            print("Ocurrió un error actualizando el costo")
    def menu(self):

        # Print our menu.
        print(BColors.WARNING + "----------------------------------------------------------------"+ BColors.ENDC)

        print(BColors.WARNING + "Bienvenido!, Al Nodo: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Cambiar el costo de enlace con un nodo")
        print(BColors.BOLD + "-2-" + BColors.ENDC, "Enviar un mensaje a un nodo")
        print(BColors.BOLD + "-3-" + BColors.ENDC, "Terminar a este nodo")
        print(BColors.BOLD + "-4-" + BColors.ENDC, "Imprimir la tabla de enrutamiento vigente")
        print(BColors.BOLD + "-5-" + BColors.ENDC, "Salir")
        print(BColors.WARNING + "----------------------------------------------------------------" + BColors.ENDC)

        user_input = input("Qué desea hacer?\n")

        if user_input == "1":
            print("Cambiando el costo de un enlace")
            self.change_cost()
            self.menu()
        elif user_input == "2":
            self.send_message()
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

    def set_false(self):
        for key in list(self.bitmap):
            self.bitmap[(key[0],key[1])] = False
    def setTrue(self, ip, port):
        self.bitmap[(ip,port)] = True
#
# port = input("port: ")
# nodoUDP = NodeUDP("127.0.0.1",int(port))
