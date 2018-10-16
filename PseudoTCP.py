
from Node import *
from socket import *
from ReachabilityTables import *
from random import *

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


class SegmentStructure():
    """docstring for SegmentStructure."""
    def __init__(self, sourcePort,destinationPort,sequenceNumber,acknowledgmentNumber,headerLength,flagACK,flagFIN,flagSYN,data):
        self.sourcePort = sourcePort
        self.destinationPort = destinationPort
        self.sequenceNumber = sequenceNumber
        self.acknowledgmentNumber = acknowledgmentNumber
        self.headerLength = headerLength
        self.flagACK = flagACK
        self.flagFIN = flagFIN
        self.flagSYN = flagSYN
        self.data = data
    def getSegment(self):
        return 2

class PseudoTCP(Node):
    """docstring for PseudoTCP."""
    def __init__(self, ip, port):
        super().__init__("pseudoTCP", ip, int(port))
        self.reachability_table = ReachabilityTables()
        self.serverQueues = {}
        self.clientQueues = {}
        self.serverPseudoTCP()

        self.menu()


    def serverPseudoTCP(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))

        
        self.threadServer = threading.Thread(target = self.listen)
        self.threadServer.daemon = True
        self.threadServer.start()

    def serverDispatcher(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        self.listen(1)
        while True:
            message, client_addr = self.server_socket.recvfrom(1024)
            print("Message Recieved")
            err = bytes([2])
            self.server_socket.sendto(err, client_addr)


    def listen(self, nConnections):
        nConnections = nConnections



    def serverThread(self):
        pass
    def accept(self):
        pass



    def clientDispatcher(self):
        pass
    def clientPseudoTCP(self,ip_destination,port_destination):
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.connect((str(ip_destination), port_destination))
        self.client_socket.send(bytes([2]))
        modified_sentence = self.client_socket.recv(1024)
        print ("From Server:" , modified_sentence)
        self.client_socket.close()

    def send_file(self):
        self.log_writer.write_log("PseudoTCP node is sending a message.", 2)

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

        #n = input("Digite el nombre del archivo que desea enviar")
        filename = "archivo.txt"


    def connect(self, destPort):
        sourcePort = self.port
        destinationPort = destPort
        sequenceNumberClient= randrange(400)
        acknowledgmentNumber = 0
        headerLength = 1
        flagACK = 0
        flagFIN = 0
        flagSYN = 1
        data = 0
        segmentStructure = SegmentStructure(sourcePort,destinationPort,sequenceNumber,acknowledgmentNumber,headerLength,flagACK,flagFIN,flagSYN,data)
        segmentToSend = segmentStructure.getSegment()
        '''
        self.client_socket.send(bytes([2]))
        try:
            self.clientQueues["1"].get(True,10)
        except Empty:
            print("GG")
        '''
    def menu(self):
        # Print our menu.
        print(BColors.WARNING + "Bienvenido!, Node: " + self.ip, ":", str(self.port) + BColors.ENDC)
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Enviar un mensaje a otro nodo")
        print(BColors.BOLD + "-2-" + BColors.ENDC, "Terminar a este nodo")
        print(BColors.BOLD + "-3-" + BColors.ENDC, "Imprimir la tabla de alcanzabilidad")
        print(BColors.BOLD + "-4-" + BColors.ENDC, "Salir")

        user_input = input("Qué desea hacer?\n")
        if user_input == "1":
            self.send_file()
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

pseudo = PseudoTCP('localhost','8080')
pseudo.clientPseudoTCP('localhost',8080)
