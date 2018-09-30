import threading
from Node import *
from ReachabilityTables import *
from TablaTCP import *
from socket import *
from texttable import *
import time


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


class NodeTCP(Node):

    def __init__(self, ip, port):
        super().__init__("pseudoBGP", ip, int(port))
        self.reachability_table = ReachabilityTables()
        self.tcp_table = TablaTCP()

        # Start our server thread, which will handle new connections.
        self.threadServer = threading.Thread(target = self.server_tcp)
        self.threadServer.daemon = True
        self.threadServer.start()
        
        # Start listening for new connections.
        self.listen()

    # Start a new server thread that will handle all connections.
    def server_tcp(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(100)
        print ("El servidor esta listo para ser usado : ", self.ip, self.port)

        while True:
            connection_socket, address = server_socket.accept()
            self.tcp_table.save_connection(address[0], address[1], connection_socket)
            thread_server_c = threading.Thread(target = self.server_tcp_thread, args=(connection_socket, address))
            thread_server_c.daemon = True
            thread_server_c.start()

    # Start a new TCP connection thread with another node.
    def server_tcp_thread(self, connection_socket, address):
        
        # Set our flag that will determine when to stop listening.
        flag = True
        
        # While the flag is true, keep on receiving messages.
        while flag:
            
            try:
                
                # Wait for a message to be received.
                message = connection_socket.recv(1024)
                
                # Case where we receive a new message.
                if int.from_bytes(message, byteorder="big") != 0 and \
                        len(message) > 1:

                    self.log_writer.write_log("TCP node received a message.", 1)
                    elements_quantity = int.from_bytes(message[:2], byteorder="big")
                    table = Texttable()
                    table.set_cols_align(["l", "r", "c","k"])
                    table.set_cols_valign(["t", "m", "b","a"])
                    table.add_row(["IP de origen", "Ip", "Máscara","Costo"])
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

                        table.add_row([address[0], ip_str, mask_str, cost])

                        # Save to our reachability table.
                        self.reachability_table.save_address(ip_str, address[0], mask_str,
                                                             cost, int(connection_socket.getpeername()[1]))
                    print (table.draw() + "\n")

                # Remove the node from the reachability table and then send a confirmation message.
                elif int.from_bytes(message, byteorder="big") == 0:

                    self.log_writer.write_log("TCP node received a terminating notification.", 1)
                    self.reachability_table.remove_address(connection_socket.getpeername()[0],
                                                           int(connection_socket.getpeername()[1]))

                    try:
                        print("Hemos recivido una notificación de terminación del nodo con dirección: "
                              + connection_socket.getpeername()[0] + " y puerto: " +
                              str(connection_socket.getpeername()[1]))
                        confirmation_message = bytes([2])
                        connection_socket.send(confirmation_message)
                        self.tcp_table.close_connection(connection_socket.getpeername()[0],
                                                        int(connection_socket.getpeername()[1]))

                        flag = False
                        print("La conexión con el nodo ha sido eliminada.")
                    except BrokenPipeError:
                        print("No se pudo enviar el mensaje de borrado satisfactorio")
                        flag = False

                # Enter here when we receive a termination notification from another node.
                elif int.from_bytes(message, byteorder="big") == 2:

                    self.log_writer.write_log("TCP node received a termination confirmation.", 1)
                    print("Recivimos mensaje de terminación del nodo con dirección: "
                          + connection_socket.getpeername()[0] + " y puerto: " +
                          str(connection_socket.getpeername()[1])
                          + ". Estamos cerrando la conexión.")
                    self.tcp_table.close_connection(connection_socket.getpeername()[0],
                                                    int(connection_socket.getpeername()[1]))

                    # Set flag to false, so that we stop listening.
                    flag = False

            except ConnectionResetError:
                '''Obtenemos el recurso que es la tabla de conexiones vivas'''
                self.tcp_table.close_connection(address[0], int(connection_socket.getpeername()[1]))
                print("La conexión se ha perdido con ", address[0], int(connection_socket.getpeername()[1]))
                flag = False

    # Send messages to other nodes.
    def send_message(self):
        print("Enviar mensaje:")

        self.log_writer.write_log("TCP node is sending a message.", 2)

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

        num = 1

        valid_input = False
        while not valid_input:
            try:
                num = int(input("Digite la cantidad de mensajes que va enviar a ese destino: "))
                valid_input = True
            except ValueError:
                print(BColors.FAIL + "Error: " + BColors.ENDC + "Entrada no númerica")

        port_destination = int(port)
        mask_destination = int(mask)
        elements_quantity = num.to_bytes(2, byteorder="big")
        byte_array = bytearray(elements_quantity)
        for i in range(0,num):

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

            # If we already have the connection, then we just send it.
            if self.tcp_table.search_connection(ip_destination, port_destination) != -1:
                self.tcp_table.search_connection(ip_destination, port_destination).send(byte_array)

            else:
                client_socket = socket(AF_INET, SOCK_STREAM)

                # Try to connect to the other node.
                try:
                    client_socket.connect((ip_destination, port_destination))
                    self.tcp_table.save_connection(ip_destination, port_destination, client_socket)
                    # Send confirmation message to the other node.
                    client_socket.send(byte_array)

                    print("Nos hemos conectado con el nodo con dirección %s y puerto %s." %
                          (ip_destination, port_destination))
                    # Create a new thread to start listening to the node.
                    thread_server_c = threading.Thread(target=self.server_tcp_thread,
                                                       args=(client_socket, {ip_destination, port_destination}))
                    thread_server_c.daemon = True
                    thread_server_c.start()

                except Exception as e:
                    print("Error al conectarnos con el nodo %s, en el puerto %s. "
                          "Debido al error %s" % (ip_destination, port_destination, e))

        except BrokenPipeError:
            print("Se perdió la conexión con el servidor")

    # Tell all nodes that we our node is being terminated.
    def terminate_node(self):

        # This variable will keep the number of attempts that are being executed
        attempts = 0

        # Wait for all connections to be closed and at least try three times.
        while attempts < 3 and len(self.tcp_table.table) > 0:

            for key in list(self.tcp_table.table):

                try:
                    print("Enviando notificación de terminación a todos los nodos.")
                    connection_socket = self.tcp_table.search_connection(key[0], key[1])
                    connection_socket.send(bytes([0]))

                except Exception:
                    print("No se pudo conectar con el nodo con dirección " + key[0] +
                          " y mascara " + str(key[1]) + ".")

            # Now we wait a little bit, and after we check that all connections are close.
            if len(self.tcp_table.table) > 0:
                time.sleep(2)
                attempts += 1
            else:
                break

        if len(self.tcp_table.table) > 0:
            print("Se intento eliminar este nodo de todas las conexiones, pero quedaron"
                  " algunas conexiones activas.")
        else:
            print("Se cerraron todas las conexiones con éxito.")

    # Show our user the possible instructions he can accomplish with our node.
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
            print("Eliminando nodo.")
            self.terminate_node()
            print("Terminando ejecucción.")
        elif user_input == "3":
            self.reachability_table.print_table()
            self.listen()
        elif user_input == "4":
            print("Terminando ejecucción.")
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.listen()

