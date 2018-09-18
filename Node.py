import socket

## Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Node:
    def __init__(self, protocol, ipNode, port):
        self.protocol = protocol
        self.ip = ipNode
        self.port = int(port)

    def __del__(self):
        print("Node was successfully deleted")

    def nodeMenu(self):
        ##Variables
        opcion = "0"
        ## Menu
        while opcion != "3":
            print(bcolors.WARNING+"You are now working with node", ip + "!" +bcolors.ENDC)
            print("What do you want to do?")
            print("1 - Enviar Mensaje ")
            print("2 - Borrar nodo ")
            print("3 - Salir")

            opcion = input("¿? \n")

            if(opcion ==  "1"):
                print("Usted quiere enviar un mensaje")
            if(opcion == "2"):
                print("Usted quiere eliminar este nodo")
                #envia mensaje con un 0 para que se borre de las tablas
                #del self
            if(opcion == "3"):
                print("Good bye!")
