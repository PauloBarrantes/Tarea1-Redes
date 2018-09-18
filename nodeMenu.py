## Imports
from Node import *
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

##Variables
nodeList = []
opcion = "0"
## Menu

while opcion != "4":
    print(bcolors.WARNING+"Welcome!" +bcolors.ENDC)
    print("What do you want to do?")
    print("1 - Enviar Mensaje ")
    print("2 - Borrar nodo ")
    print("3 - Salir")

    opcion = input("¿? \n")

    if(opcion ==  "1"):
        print("Digite el nombre del archivo que contiene el mensaje")
        fileName = input("")
        file = open(fileName, "r")
        print(command)
        commands = command.split()
        print(commands)
        if(commands[0] == "creaNodo"):
            if(commands[1] == "-pseudoBGP"):
                newNode = NodeTCP(commands[2],commands[3])
                nodeList.append(newNode)
            if(commands[1] == "-intAS"):
                newNode = NodeUDP(commands[2],commands[3])
                nodeList.append(newNode)
        else:
            print("Invalid syntax, please follow the structure")
    if(opcion == "2"):
        print("Which node do you want to delete? (Type index)")
        for node in nodeList:
            counter = 1
            print(counter, "- Address:", node.direccionNodo, ", Port:", node.puertoNodo)
            ++counter
        index = int(input(""))
        if(index > 0 and index <= len(nodeList)):
            nodeList[index-1].broadcastClosure()
            del nodeList[index-1]
        else:
            print("Invalid index.")
    if(opcion == "3"):
        pass
    if(opcion == "4"):
        print("Good bye!")

#Node('10.1.138.89',8080)
