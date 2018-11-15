from Node import *
from socket import *
from NeighborsTable import *
from ReachabilityTables import *
from encoder_decoder import *
import time
TIMEOUT_UPDATES  = 30
TIMEOUT_ACK = 2

'''CONSTANTS'''
MESSAGE_TYPE_UPDATE = 1
MESSAGE_TYPE_ALIVE = 2
MESSAGE_TYPE_I_AM_ALIVE = 3
MESSAGE_TYPE_FLOOD = 4
MESSAGE_TYPE_DATA = 5
MESSAGE_TYPE_COST_CHANGE = 6
MESSAGE_TYPE_CHANGE_DEATH = 7

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

        # Start server thread.
        self.threadServer = threading.Thread(target = self.server_udp)

        # Continue the server, even after our main thread dies.
        self.threadServer.daemon = True
        self.threadServer.start()

        self.request_neighbors()

        time.sleep(5)

        print("PASAMOS EL REQUEST ")

        self.aliveMessages()

        self.threadUpdates = threading.Thread(target = self.sendUpdates)
        # Continue the server, even after our main thread dies.
        self.threadUpdates.daemon = True
        self.threadUpdates.start()

        # Run our menu.
        self.menu()

    def server_udp(self):

        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        print ("El servidor esta listo: ", self.ip, self.port)

        while True:
            message, client_addr = self.server_socket.recvfrom(1024)

            messageType = int(message[0])

            if messageType == MESSAGE_TYPE_ALIVE:
                print("MESSAGE_TYPE_ALIVE")
                # Recibir ip,mask,port
                ip_bytes = message[1:5]
                mask = message[5]
                port_bytes = message[6:8]

                ip = list(ip_bytes)
                ip_str = ""
                for byte in range(0,len(ip)):
                    if(byte < len(ip)-1):
                        ip_str += str(ip[byte])+"."
                    else:
                        ip_str += str(ip[byte])
                port = int.from_bytes(port_bytes, byteorder="big")

                # Guardar en tabla de vecinos que está vivo.
                self.neighbors_table.save_address(ip_str, mask, port, cost, 1)

                message = bytearray(MESSAGE_TYPE_I_AM_ALIVE.to_bytes(3, byteorder="big"))

                self.server_socket.sendto(message, client_addr)


            elif messageType == MESSAGE_TYPE_UPDATE:
                print("MESSAGE_TYPE_UPDATE")

            elif messageType == 2:

                updateRT(messageRT)

            else:
                print("gg")

    def updateRT(self, messageRT):
        elements_quantity = int.from_bytes(messageRT[:3], byteorder="big")
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
            self.reachability_table.save_address(ip_str, mask, port, cost, client_addr[0], mask, int(client_addr[1]))
    def sendUpdates(self):
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
                    reach_counter = 0
                    for key2 in list(self.reachability_table.reach_table):
                        if key2 != key:
                            reach_counter += 1
                            message.extend(bytearray(bytes(map(int, (key2[0]).split(".")))))
                            message.extend(key2[1].to_bytes(1, byteorder="big"))
                            message.extend((key2[2]).to_bytes(2, byteorder="big"))
                            message.extend(self.reachability_table.reach_table.get(key2)[0]).to_bytes(3, byteorder="big")

                    message[0:0] = reach_counter.to_bytes(2, byteorder="big")

                    threadSendUpdates = threading.Thread(target = self.threadSendUpdates, args=(ip, mask, port, message))
                    threadSendUpdates.daemon = True
                    threadSendUpdates.start()




    def threadSendUpdates(self, ip, mask, port, reachability_table):
        try:

            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.connect((str(ipDest), portDest))
            client_socket.sendall(reachability_table)
            client_socket.close()

        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")
            self.neighbors_table.save_address(self, ipDest, maskDest, portDest, cost, 0)



    # Request neighbors
    def request_neighbors(self):
        central_ip = "127.0.0.1"
        default_mask = 16
        central_port = 9000

        byte_message = bytearray(bytes(map(int, (self.ip).split("."))))
        byte_message.extend(default_mask.to_bytes(1, byteorder="big"))
        byte_message.extend((self.port).to_bytes(2, byteorder="big"))

        try:
            self.client_socket = socket(AF_INET, SOCK_DGRAM)
            self.client_socket.connect((str(central_ip), central_port))
            self.client_socket.send(byte_message)
            neighbors_message = self.client_socket.recv(1024)
            elements_quantity = int.from_bytes(neighbors_message[:2], byteorder="big")
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
                self.neighbors_table.save_address(ip_str, mask, port, cost, 0)
            self.client_socket.close()
            self.neighbors_table.print_table()
        except BrokenPipeError:
            print("Se perdió la conexión con el nodo central")




    # Send messages to another node.
    def aliveMessages(self):

        for key in list(self.neighbors_table.neighbors):
            ip = key[0]
            mask = key[1]
            port = key[2]


            message = bytearray(MESSAGE_TYPE_ALIVE.to_bytes(1, byteorder="big"))


            threadAliveMessage = threading.Thread(target = self.threadAliveMessage, args=(ip, mask, port, message))
            threadAliveMessage.daemon = True
            threadAliveMessage.start()

        time.sleep(1)

    # Thread manda mensajes a cada vecino y espera el ACK

    def threadAliveMessage(self, ipDest, maskDest, portDest, message):
        try:
            print("hagamo el intento")
            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.connect((str(ipDest), portDest))
            client_socket.send(message)
            client_socket.settimeout(TIMEOUT_ACK)
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
