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

    
