from Node import *
from socket import *
from NeighborsTable import *
from ReachabilityTables import *
from encoder_decoder import *
import time
TIMEOUT  = 30
TIMEOUT_ACK = 3

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

        # Run our menu.
        self.menu()

    def server_udp(self):

        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        print ("El servidor esta listo: ", self.ip, self.port)

        while True:
            message, client_addr = self.server_socket.recvfrom(1024)
            if int.from_bytes(message, byteorder="big") != 0:

                self.log_writer.write_log("UDP node received a message.", 1)



            else:

                # Remove from our reachability table.
                self.reachability_table.remove_address(client_addr[0], int(client_addr[1]))
            print("Message Recieved")
            err = bytes([2])
            self.server_socket.sendto(err, client_addr)

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
            print(neighbors_message)
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
                self.neighbors_table.save_address(ip_str, mask, port, cost)
            self.neighbors_table.print_table()
            self.client_socket.close()
        except BrokenPipeError:
            print("Se perdió la conexión con el nodo central")

    # Send messages to another node.
    def enviarMensajesANodos(self):

        for key in list(self.neighbors_table.neighbors):
            print(key)
            threadServer = threading.Thread(target = self.mensajeNodo, args=(ip, mask, port, mensaje))


    def mensajeNodo(self, ipDest, maskDest, portDest, mensaje):
        try:
            self.client_socket = socket(AF_INET, SOCK_DGRAM)
            self.client_socket.connect((str(ip_destination), port_destination))
            self.client_socket.send(byte_array)
            modified_sentence = self.client_socket.recv(1024)
            print ("From Server:" , modified_sentence)
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
            self.menu()
        elif user_input == "2":
            print ("Eliminando nodo - need a fix")
            self.terminate_node()
        elif user_input == "3":
            self.reachability_table.print_table()
            self.menu()
        elif user_input == "4":
            print("Terminando ejecucción.")
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.menu()

nodoUDP = NodeUDP("127.0.0.1",8080)
nodoUDP.request_neighbors()
