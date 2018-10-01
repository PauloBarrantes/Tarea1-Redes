import ipaddress
from LogWriter import *


class Node:

    def __init__(self, protocol, ipNode, port):
        self.protocol = protocol
        self.ip = ipNode
        self.port = int(port)
        self.log_writer = LogWriter()

    def __del__(self):
        print("Node was successfully deleted")

    # Validate the user's node input.
    def validate_ip(self, ip):

        # Validate the ip address.
        try:
            ipaddress.ip_address(ip)
        except ValueError as err:
            print("La dirección ip ingresada (%s) es erronear. Error: %s." %
                  (ip, err))
            return False

        return True

    # Validate the user's input mask.
    def validate_mask(self, mask):

        # Validate the mask.
        try:
            num = int(mask)
        except ValueError:
            print("La mascara tiene quer ser una entrada númerica.")
            return False

        if num > 256 or num < 0:
            print("La mascara tiene que ser un número entre 0 y 256.")
            return False

        return True

    # Validate the user's input port.
    def validate_port(self, port):

        # Validate the port.
        try:
            num = int(port)
        except ValueError:
            print("El puerto tiene quer ser una entrada númerica.")
            return False

        if num > 63535 or num < 80:
            print("El puerto tiene quer ser un número entre 63535 y 80.")
            return False

        return True

    # Validate the user's input cost.
    def validate_cost(self, cost):

        # Validate the cost.
        try:
            num = int(cost)
        except ValueError:
            print("El puerto tiene quer ser una entrada númerica.")
            return False

        if num > 16777216 or num < 0:
            print("El puerto tiene quer ser un número entre 16,777,216 y 0.")
            return False

        return True

    def validate_ip_network(self, ip, mask):

        # Validate the ip address.
        try:
            ipaddress.ip_network(ip+"/"+mask)
        except ValueError as err:
            print("La dirección ip ingresada (%s) es erronear. Error: %s." %
                  (ip+"/"+mask, err))
            return False

        return True