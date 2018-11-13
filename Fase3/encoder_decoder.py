from Node import *
from socket import *
from NeighborsTable import *
from ReachabilityTables import *



def encodeRT(reachabilityTables):
    pass

def decodeRT(message):
    elements_quantity = int.from_bytes(message[:2], byteorder="big")
    for n in range(0,elements_quantity):
        ip_bytes = message[2+(n*8):6+(n*8)]
        mask_bytes = message[6+(n*8)]
        cost_bytes = message[7+(n*8):10+(n*8)]
        ip = list(ip_bytes)
        ip_str = ""
        for byte in range(0,len(ip)):
            if(byte < len(ip)-1):
                ip_str += str(ip[byte])+"."
            else:
                ip_str += str(ip[byte])
        mask_str = int(mask_bytes)
        cost = int.from_bytes(cost_bytes,byteorder="big")

        decodedMessage = [ip_str,mask,cost]
        #self.reachability_table.save_address(ip_str, client_addr[0],mask_str, cost, int(client_addr[1]))
