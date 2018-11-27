from Node import *
from socket import *
from NeighborsTable import *
from ReachabilityTables import *



def encodeRT(key, message, reachabilityTable):
    reach_counter = 0
    for key2 in list(reachabilityTable.reach_table):
        if key2 != key:
            reach_counter += 1
            message.extend(bytearray(bytes(map(int, (key2[0]).split(".")))))
            message.extend(reachabilityTable.reach_table.get(key2)[5].to_bytes(1, byteorder="big"))
            message.extend((key2[1]).to_bytes(2, byteorder="big"))
            message.extend(reachabilityTable.reach_table.get(key2)[0].to_bytes(3, byteorder="big"))
    message[1:3] = reach_counter.to_bytes(2,byteorder="big")


def decodeRT(messageRT):
    decoded_RT = []

    elements_quantity = int.from_bytes(messageRT[1:3], byteorder="big")
    for n in range(0, elements_quantity):
        decoded_tuple = []
        ip_bytes = messageRT[3+(n*10):7+(n*10)]
        mask = messageRT[7+(n*10)]
        port_bytes = messageRT[8+(n*10):10+(n*10)]
        cost_bytes = messageRT[10+(n*10):13+(n*10)]
        ip = list(ip_bytes)
        ip_str = ""
        for byte in range(0,len(ip)):
            if(byte < len(ip)-1):
                ip_str += str(ip[byte])+"."
            else:
                ip_str += str(ip[byte])
        port = int.from_bytes(port_bytes, byteorder="big")
        cost = int.from_bytes(cost_bytes, byteorder="big")

        decoded_tuple.append(ip_str)
        decoded_tuple.append(mask)
        decoded_tuple.append(port)
        decoded_tuple.append(cost)

        decoded_RT.append(decoded_tuple)

    return decoded_RT

def encodeNeighbors(ipRequest, maskRequest, portRequest, neighbors):
    neighbors_message = bytearray()
    neighbor_counter = 0
    print("Vamos a revisar vecinos", len(neighbors))
    for i in range (0,len(neighbors)):
        if neighbors[i][0] == ipRequest and int(neighbors[i][1]) == maskRequest and int(neighbors[i][2]) == portRequest:
            print("Vecino A - B")
            neighbor_counter += 1
            neighbors_message.extend(bytearray(bytes(map(int, neighbors[i][3].split(".")))))
            neighbors_message.extend(int(neighbors[i][4]).to_bytes(1, byteorder="big"))
            neighbors_message.extend(int(neighbors[i][5]).to_bytes(2, byteorder="big"))
            neighbors_message.extend(int(neighbors[i][6]).to_bytes(3, byteorder="big"))
        elif neighbors[i][3] == ipRequest and int(neighbors[i][4]) == maskRequest and int(neighbors[i][5]) == portRequest:
            print("Vecino B - A")
            neighbor_counter += 1
            neighbors_message.extend(bytearray(bytes(map(int, neighbors[i][0].split(".")))))
            neighbors_message.extend(int(neighbors[i][1]).to_bytes(1, byteorder="big"))
            neighbors_message.extend(int(neighbors[i][2]).to_bytes(2, byteorder="big"))
            neighbors_message.extend(int(neighbors[i][6]).to_bytes(3, byteorder="big"))

    neighbors_message[0:0] = neighbor_counter.to_bytes(2, byteorder="big")

    return neighbors_message

def decodeNeighbors(neighbors_message):
    decoded_table = []

    elements_quantity = int.from_bytes(neighbors_message[:2], byteorder="big")

    for n in range(0, elements_quantity):
        decoded_tuple = []

        ip_bytes = neighbors_message[2+(n*10):6+(n*10)]

        mask = neighbors_message[6+(n*10)]
        port_bytes = neighbors_message[7+(n*10):9+(n*10)]
        cost_bytes = neighbors_message[9+(n*10):12+(n*10)]
        ip = list(ip_bytes)
        ip_str = ""
        for byte in range(0,len(ip)):
            if (byte < len(ip)-1):
                ip_str += str(ip[byte])+"."
            else:
                ip_str += str(ip[byte])
        print(ip_str)
        port = int.from_bytes(port_bytes, byteorder="big")
        cost = int.from_bytes(cost_bytes, byteorder="big")

        decoded_tuple.append(ip_str)
        decoded_tuple.append(mask)
        decoded_tuple.append(port)
        decoded_tuple.append(cost)
        decoded_table.append(decoded_tuple)
    return decoded_table

def check_message(message, ip, port):
    ip_dest = message[1:5]
    ip = list(ip_dest)
    ip_str = ""
    for byte in range(0,len(ip)):
        if(byte < len(ip)-1):
            ip_str += str(ip[byte])+"."
        else:
            ip_str += str(ip[byte])
    port_bytes = message[5:7]
    port_dest = int.from_bytes(port_bytes, byteorder="big")
    elements_quantity = int.from_bytes(messageRT[7:9], byteorder="big")

    return self.ip == ip_str and port_dest == self.port
