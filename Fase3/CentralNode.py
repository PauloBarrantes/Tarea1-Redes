from Node import *
from socket import *
from texttable import *
import csv
'''
    Central Node
        IP: 127.0.0.1
        Port: 9000
'''


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


class CentralNode(Node):
    def __init__(self, ip, port):
        super().__init__("intAS", ip, int(port))

        '''
            Neighbors Table

            0 -> IP A
            1 -> Mask A
            2 -> Port A
            3 -> IP B
            4 -> Mask B
            5 -> Port B
            6 -> Cost between A and B
        '''
        self.neighbors = []
        self.extract_neighbors()
        # Start server thread.
        self.threadServer = threading.Thread(target = self.server_central)

        # Continue the server, even after our main thread dies.
        self.threadServer.daemon = True
        self.threadServer.start()

        self.menu()



    def server_central(self):

        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        print ("El servidor central está listo: ", self.ip, self.port)

        while True:
            message, client_addr = self.server_socket.recvfrom(1024)
            if int.from_bytes(message, byteorder="big") != 0:
                print("PRUEBA: ", client_addr[0],"-",client_addr[1])
                #elf.log_writer.write_log("Central Node received a request.", 1)
                neighborsList = []

                ip_bytes = message[0:4]
                maskRequest = message[4]
                portBytes = message[5:8]


                ip = list(ip_bytes)
                ipRequest = ""
                for byte in range(0,len(ip)):
                    if(byte < len(ip)-1):
                        ipRequest += str(ip[byte])+"."
                    else:
                        ipRequest += str(ip[byte])
                portRequest = int.from_bytes(portBytes,byteorder="big")

                neighbors_message = encodeNeighbors(ipRequest, maskRequest, portRequest, self.neighbors)
                self.server_socket.sendto(neighbors_message, client_addr)

            else:
                print("Se han comunicado conmigo, pero no respetaron el protocolo :v")



    def extract_neighbors(self):
        with open('neighbors.csv', newline='') as csvfile:
            # We obtain neighbor from csv file
            neighborsCSV = csv.reader(csvfile, delimiter=';', quotechar='|')

            # and fill a structure with each neighbor pair
            for row in neighborsCSV:
                neighbor = []
                neighbor.append(row[0])
                neighbor.append(row[1])
                neighbor.append(row[2])
                neighbor.append(row[3])
                neighbor.append(row[4])
                neighbor.append(row[5])
                neighbor.append(row[6])
                self.neighbors.append(neighbor)


    def printNeighbors(self, neighborsList):
        print("Lista de Vecinos")
        table = Texttable()
        table.set_cols_align(["c", "c","c","c", "c","c","c"])
        table.set_cols_valign(["m", "m","m","m", "m","m","m"])
        table.add_row([
        "ip A",
        "Máscara A",
        "Puerto A",
        "ip B",
        "Máscara B",
        "Puerto B",
        "Costo "])

        for i in range (0,len(neighborsList)):
            ipA = neighborsList[i][0]
            maskA = neighborsList[i][1]
            portA = neighborsList[i][2]
            ipB = neighborsList[i][3]
            maskB = neighborsList[i][4]
            portB = neighborsList[i][5]
            cost = neighborsList[i][6]
            table.add_row([ipA,maskA,portA,ipB, maskB, portB,cost])


        print (table.draw() + "\n")
    def menu(self):
        print(BColors.OKGREEN + "Instrucciones: " + BColors.ENDC)
        print(BColors.BOLD + "-1-" + BColors.ENDC, "Para acabar con la vida de este nodo central :(")
        user_input = input("Qué desea hacer?\n")
        if user_input == "1":
            print("Adios - lease con voz de Walter")
        else:
            self.menu()
node = CentralNode("127.0.0.1",9000)
