from Node import *
from socket import *
from ReachabilityTables import *


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

        # Start server thread.
        self.threadServer = threading.Thread(target = self.server_udp)

        # Continue the server, even after our main thread dies.
        self.threadServer.daemon = True
        self.threadServer.start()

        # Run our menu.
        self.listen()

    def server_udp(self):

        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        print ("El servidor esta listo para ser usado : ", self.ip, self.port)

        while True:
            message, client_addr = self.server_socket.recvfrom(1024)
            if int.from_bytes(message, byteorder="big") != 0:

                self.log_writer.write_log("UDP node received a message.", 1)

                elements_quantity = int.from_bytes(message[:2], byteorder="big")
                for n in range(0,elements_quantity):
                    ip_bytes = message[2+(n*8):6+(n*8)]
                    mask = message[6+(n*8)]
                    cost_bytes = message[7+(n*8):10+(n*8)]
                    ip = list(ip_bytes)
                    ip_str = ""
                    for byte in range(0,len(ip)):
                        if(byte < len(ip)-1):
                            ip_str += str(ip[byte])+"."
                        else:
                            ip_str += str(ip[byte])
                    mask_str = str(mask)
                    cost = int.from_bytes(cost_bytes,byteorder="big")
                    self.reachability_table.save_address(ip_str, client_addr[0],
                                                         mask_str, cost, int(client_addr[1]))

            else:

                # Remove from our reachability table.
                self.reachability_table.remove_address(client_addr[0], int(client_addr[1]))
            print("Message Recieved")
            err = bytes([2])
            self.server_socket.sendto(err, client_addr)

    # Send messages to another node.
    def send_message(self):

        self.log_writer.write_log("UDP node is sending a message.", 2)

        # Variables that we will use to keep the user's input.
        port = ""
        mask = ""
        ip_destination = ""

        # Variable to check each input of the user.
        valid_input = False
        while not valid_input:
            ip_destination = input("Digite la ip de destino a la que desea enviar: ")
            valid_input = self.validate_ip(ip_destination)

        valid_input = False
        while not valid_input:
            mask = input("Digite la máscara de destino a la que desea enviar: ")
            valid_input = self.validate_mask(mask)

        valid_input = False
        while not valid_input:
            port = input("Digite el puerto de destino a la que desea enviar: ")
            valid_input = self.validate_port(port)

        n = input("Digite la cantidad de mensajes que va enviar a ese destino: ")
        num = 1

        valid_input = False
        while not valid_input:
            try:
                num = int(n)
                valid_input = True
            except ValueError:
                print(BColors.FAIL + "Error: " + BColors.ENDC + "Entrada no númerica")

        port_destination = int(port)
        mask_destination = int(mask)
        elements_quantity = num.to_bytes(2, byteorder="big")
        byte_array = bytearray(elements_quantity)
        for i in range(0, num):

            ip_message = ""
            mask_message = ""
            cost_message = ""

            valid_input = False
            while not valid_input:
                ip_message = input("Digite la ip de destino a la que desea enviar: ")
                valid_input = self.validate_ip(ip_message)

            valid_input = False
            while not valid_input:
                mask_message = input("Digite la máscara de destino a la que desea enviar: ")
                valid_input = self.validate_mask(mask_message)

            valid_input = False
            while not valid_input:
                cost_message = input("Digite un costo: ")
                valid_input = self.validate_cost(cost_message)

            byte_array.extend(bytearray(bytes(map(int, ip_message.split(".")))))
            byte_array.extend((int(mask_message)).to_bytes(1, byteorder="big"))
            byte_array.extend(int(cost_message).to_bytes(3, byteorder="big"))

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

    def listen(self):

        # Print our menu.
        print(BColors.WARNING + "Bienvenido!, Node: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Enviar un mensaje a otro nodo")
        print(BColors.BOLD + "-2-" + BColors.ENDC, "Terminar a este nodo")
        print(BColors.BOLD + "-3-" + BColors.ENDC, "Imprimir la tabla de alcanzabilidad")
        print(BColors.BOLD + "-4-" + BColors.ENDC, "Salir")

        user_input = input("Qué desea hacer?\n")
        if user_input == "1":
            self.send_message()
            self.listen()
        elif user_input == "2":
            print ("Eliminando nodo")
            self.terminate_node()
        elif user_input == "3":
            self.reachability_table.print_table()
            self.listen()
        elif user_input == "4":
            print("Terminando ejecucción.")
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.listen()

