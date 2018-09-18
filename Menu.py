
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
## Menu

print(bcolors.WARNING+"Welcome!" +bcolors.ENDC)
print("What do you want to do?")
print("1 - Create a node ")
print("2 - Delete a node ")
print("3 - Communicate nodes")

opcion = input("¿? \n")

if(opcion ==  "1")
    print("Please create a node with the following structure: creaNodo -<pseudoBGP/intAS> <IPAddress> <portNumber>")
    command = input("\n")
    command.split(" ")
    if(command[0] == "creaNodo")
        if(command[1] == "-pseudoBGP")
            NodeTCP(command[2],command[3])
        if(command[1] == "-intAS")
            NodeUDP(command[2],command[3])
    else:
        print("Invalid syntax, please follow the structure")


#Node('10.1.138.89',8080)
