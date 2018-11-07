import sys
from NodeTCP import *
from NodePseudoTCP import *
from NodeUDP import *


class bcolors:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

cantidadArgumentos = len(sys.argv)

if cantidadArgumentos != 4:
    print(bcolors.FAIL+"Error: "+bcolors.ENDC+"Número incorrecto de argumentos")
else:
    typeNode = sys.argv[1]
    ip = sys.argv[2]
    splitIP = ip.split(".")
    if int(splitIP[0]) >= 0 and int(splitIP[0]) <= 255 and int(splitIP[1]) >= 0 and int(splitIP[1]) <= 255 and int(splitIP[2]) >= 0 and int(splitIP[2]) <= 255 and int(splitIP[3]) >= 0 and int(splitIP[3]) <= 255:
        port = int(sys.argv[3])
        if typeNode == "-pseudoBGP":
            NodeTCP(ip, port)
        elif typeNode == "-intAS":
            NodeUDP(ip, port)
        elif typeNode == "-pseudoTCP":
            NodePseudoTCP(ip, port)
        else:
            print(bcolors.FAIL+"Error: "+bcolors.ENDC+"Digitó mal el tipo de nodo")
    else:
        print(bcolors.FAIL+"Error: "+bcolors.ENDC+"Ocurrió un error con la dirección ip")
