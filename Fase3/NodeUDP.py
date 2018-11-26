from Node import *
from socket import *
from NeighborsTable import *
from ReachabilityTables import *
from encoder_decoder import *
import time


'''TIMEOUTS'''

TIMEOUT_UPDATES  = 30
TIMEOUT_ACK = 2
TIMEOUT_ALIVEMESSAGES = 120

'''CONSTANTS'''
DEFAULT_MASK = 16

MESSAGE_TYPE_UPDATE = 1
MESSAGE_TYPE_ALIVE = 2
MESSAGE_TYPE_I_AM_ALIVE = 3
MESSAGE_TYPE_FLOOD = 4
MESSAGE_TYPE_DATA = 5
MESSAGE_TYPE_COST_CHANGE = 6
MESSAGE_TYPE_CHANGE_DEATH = 7

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

        self.node_socket = socket(AF_INET, SOCK_DGRAM)
        self.node_socket.bind((self.ip, self.puerto))


        # Continue the server, even after our main thread dies.


        #We request neighborts to central node
        self.request_neighbors()


        # Start server thread.
        self.threadListener = threading.Thread(target = self.listener)
        self.threadListener.daemon = True
        self.threadListener.start()

        self.threadAliveMessage = threading.Thread(target = self.aliveMessages)
        self.threadAliveMessage.daemon = True
        self.threadAliveMessage.start()


        self.threadUpdates = threading.Thread(target = self.sendRT)
        # Continue the server, even after our main thread dies.
        self.threadUpdates.daemon = True
        self.threadUpdates.start()

        # Run our menu.
        self.menu()

    def listener(self):

        print ("We are listening in ", self.ip, self.port)

        while True:
            message, client_addr = self.node_socket.recvfrom(1024)

            messageType = int(message[0])
            if messageType ==  MESSAGE_TYPE_UPDATE:

                decoded_RT = decodeRT(message)

                for i in len(0,decoded_RT):
                    self.reachability_table.save_address(decodeRT[i][0], decodeRT[i][1], decodeRT[i][2], decodeRT[i][3], client_addr[0], DEFAULT_MASK, int(client_addr[1]))

            elif messageType == MESSAGE_TYPE_ALIVE:
                print("MESSAGE_TYPE_ALIVE")
                # Recibir ip,mask,port

                # Guardar en tabla de vecinos que está vivo.
                self.neighbors_table.save_address(client_addr[0], DEFAULT_MASK, int(client_addr[0]), cost, True)

                message = bytearray(MESSAGE_TYPE_I_AM_ALIVE.to_bytes(3, byteorder="big"))

                self.node_socket.sendto(message, client_addr)


            elif messageType == MESSAGE_TYPE_I_AM_ALIVE:
                print("ACK")


            else:
                print("gg")

    def sendRT(self):
        while True:
            time.sleep(TIMEOUT_UPDATES)

            for key in list(self.neighbors_table.neighbors):
                if self.neighbors_table.is_awake(key[0],key[1],key[2]) == 1:
                    ip = key[0]
                    mask = key[1]
                    port = key[2]
                    cost = self.neighbors_table.neighbors.get(key)[0]

                    print("Ip:" + ip + "mask: "+ str(mask) + "port: " +str(port))
                    print(costo)

                    message = bytearray(MESSAGE_TYPE_UPDATE.to_bytes(1, byteorder="big"))

                    encoded_RT = encodeRT(key, message, reachability_table)

                    threadSendRT = threading.Thread(target = self.threadSendRT, args=(ip, mask, port, message))
                    threadSendRT.daemon = True
                    threadSendRT.start()




    def threadSendRT(self, ip, mask, port, reachability_table):
        try:

            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.connect((str(ipDest), portDest))
            client_socket.sendall(reachability_table)
            client_socket.close()

        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")
            self.neighbors_table.save_address(self, ipDest, maskDest, portDest, cost, False)



    # Request neighbors
    def request_neighbors(self):

        byte_message = bytearray(bytes(map(int, (self.ip).split("."))))
        byte_message.extend(DEFAULT_MASK.to_bytes(1, byteorder="big"))
        byte_message.extend((self.port).to_bytes(2, byteorder="big"))

        try:
            self.client_socket = socket(AF_INET, SOCK_DGRAM)
            self.client_socket.connect((str(CENTRAL_IP), CENTRAL_PORT))
            self.client_socket.send(byte_message)
            neighbors_message = self.client_socket.recv(1024)

            decoded_table = decodeNeighbors(neighbors_message)
            for i in len(0,decoded_table):
                self.neighbors_table.save_address(decoded_table[i][0], decoded_table[i][1], decoded_table[i][2], decoded_table[i][3], 0)

            self.client_socket.close()
            self.neighbors_table.print_table()
        except BrokenPipeError:
            print("Se perdió la conexión con el nodo central")




    # Send messages to another node.
    def aliveMessages(self):
        while true:
            for key in list(self.neighbors_table.neighbors):
                ipNeighbor = key[0]
                maskipNeighbor = key[1]
                portipNeighbor = key[2]


                message = bytearray(MESSAGE_TYPE_ALIVE.to_bytes(1, byteorder="big"))


                threadAliveMessage = threading.Thread(target = self.threadAliveMessage, args=(ipNeighbor, maskipNeighbor, portipNeighbor, message))
                threadAliveMessage.daemon = True
                threadAliveMessage.start()
            time.sleep(TIMEOUT_ALIVEMESSAGES)

    # Thread manda mensajes a cada vecino y espera el ACK

    def threadAliveMessage(self, ipDest, maskDest, portDest, message):
        try:


            node_socket.sendto(message)
            message = ""
            try:
                message = client_socket.recv(1024)
                print("El nodo"+ ipDest + " - " + str(portDest) +" está vivo!")
                self.reachability_table.save_address(ipDest, maskDest,portDest, cost, ipDest, maskDest, portDest)

                self.neighbors_table.save_address(self, ipDest, maskDest, portDest, cost, 1)

            except timeout as e:
                print("Timeout Exception: ",e)
            except ConnectionRefusedError as e :
                print("ConnectionRefusedError: ", e)
            self.client_socket.close()
        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")

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
        mask_destination = int(mask)
        elements_quantity = num.to_bytes(2, byteorder="big")
        byte_array = bytearray(elements_quantity)

    def terminate_node(self):
        print("Eliminado el nodo.")

    def menu(self):

        # Print our menu.
        print(BColors.WARNING + "Bienvenido!, Al Nodo: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Cambiar el costo de enlace con un nodo")
        print(BColors.BOLD + "-2-" + BColors.ENDC, "Terminar a este nodo")
        print(BColors.BOLD + "-3-" + BColors.ENDC, "Imprimir la tabla de enrutamiento vigente")
        print(BColors.BOLD + "-4-" + BColors.ENDC, "Salir")

        user_input = input("Qué desea hacer?\n")
        if user_input == "1":
            print("Cambiando el costo de un enlace")
            self.aliveMessages()
            self.menu()
        elif user_input == "2":
            print ("Eliminando nodo - need a fix")

            self.menu()
        elif user_input == "3":
            self.reachability_table.print_table()
            self.neighbors_table.print_table()
            self.menu()
        elif user_input == "4":
            print("Terminando ejecucción.")
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.menu()

port = input("port: ")
nodoUDP = NodeUDP("127.0.0.1",int(port))
