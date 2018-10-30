from Node import *
from pseduotcp.MessageDecoder import *
from pseduotcp.PseudoTCPConnectionTable import *
from pseduotcp.PseudoTCPThread import *

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


class NodePseudoTCP(Node):

    def __init__(self, ip, port):
        super().__init__("pseudoTCP", ip, int(port))

        # Add a new pseudo tcp connection table.
        self.pseudo_tcp_connection_table = PseudoTCPConnectionTable.PseudoTCPConnectionTable()

        # Start server thread.
        self.threadServer = threading.Thread(target = self.server_pseudo_tcp)

        # Continue the server, even after our main thread dies.
        self.threadServer.daemon = True
        self.threadServer.start()

        # Run our menu.
        self.listen()

    def server_pseudo_tcp(self):

        # First, we need to bind our node to it's respective socket.
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        print ("El servidor esta listo para ser usado : ", self.ip, self.port)

        # Set our flag that will determine when to stop listening.
        flag = True

        while flag:

            # Here our dispatcher will listen for connections and determine what to do with it.
            message, client_addr = self.server_socket.recvfrom(1024)

            # First, we must decode our message and then check if the connection
            # already exist in our connection table.
            decoded_message = MessageDecoder.decode_message(message)
            entry = self.pseudo_tcp_connection_table.search_connection(decoded_message.source_ip,
                                                                       decoded_message.source_port)

            # If exist, then send the decoded message to the respective thread queue.
            # Else, we create a new thread and send the message to it.
            if entry:
                entry[0].thread_queue.put(decoded_message)
            else:

                # Create the new thread that will manage the connection.
                pseudo_tcp_thread = PseudoTCPThread(self.pseudo_tcp_connection_table, decoded_message.source_ip,
                                                    "32", decoded_message.source_port, self.ip, self.port, "file.txt")

                # Start the connection.
                pseudo_tcp_thread.start()
                pseudo_tcp_thread.thread_queue.put(decoded_message)

    # Send messages to another node.
    def send_message(self):

        self.log_writer.write_log("Pseudo TCP node is sending a message.", 2)

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

        port_destination = int(port)
        mask_destination = int(mask)

        if self.pseudo_tcp_connection_table.search_connection(ip_destination, port_destination):
            print("La conexión con el nodo con dirección ", ip_destination,
                  " y puerto ", port_destination, " ya existe y se esta transfiriendo archivos.")
        else:

            # Set up our new start connection message.
            message = MessagePseudoTCP.MessagePseudoTCP()
            message.set_flags(True, False, False, False, False, False)
            message.set_destination(ip_destination, port_destination, mask_destination)
            message.set_source(self.ip, self.port)
            message.set_message("", 0)

            # Create the new thread that will manage the connection.
            pseudo_tcp_thread = PseudoTCPThread(self.pseudo_tcp_connection_table, ip_destination, mask_destination,
                                                port_destination, self.ip, self.port, "file.txt")

            # Start the connection.
            pseudo_tcp_thread.daemon = True
            pseudo_tcp_thread.start()
            pseudo_tcp_thread.thread_queue.put(message)

    # Terminate node and send all the connections to stop.
    def terminate_node(self):
        print("Eliminando el nodo.")

        thread_list = []

        # Send a message to stop to all connections.
        for key in self.pseudo_tcp_connection_table.pseudo_tcp_connection_table:

            # Check if the entry exist, if it does, send the message.
            entry = self.pseudo_tcp_connection_table.search_connection(key[0], key[1])
            if entry is not False:
                entry[0].thread_queue.put(-1)
                thread_list.append(entry[0])

        print("Todas las conexiones se mandaron a cerrar. Esperando confirmación.")

        # Now wait for all threads to finish.
        for thread in thread_list:
            thread.join()

        print("Conexiones cerradas con éxito. Terminando el nodo.")

    def listen(self):

        # Print our menu.
        print(BColors.WARNING + "Bienvenido!, Node: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Enviar un archivo a otro nodo")
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
            self.listen()
        elif user_input == "4":
            print("Terminando ejecucción.")
            self.terminate_node()
        else:
            print("Por favor, escoja alguna de las opciones.")
            self.listen()