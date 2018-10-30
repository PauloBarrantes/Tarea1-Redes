import ipaddress


# Structure that will save our message information.
class MessagePseudoTCP:

    # Here we will save all our flags. (We will be using bytes to make the interpretation)
    # First two bits will stay on 0. They won't be used.
    # Third bit, SYN flag that tell us we want to start a new connection, if found on 1.
    # Fourth bit, closure flag, if it we found it at 1, it means we need to close the connection.
    # Fifth bit, SN.
    # Sixth bit, RN.
    # Seventh bit, flag that tell us the beginning of the message.
    # Eighth bit, flag that tell us the ending of the message.
    syn_flag = False
    closure_flag = False
    sn_flag = False
    rn_flag = False
    first_package_flag = False
    last_package_flag = False
    # Destination IP.
    # IP where our message or response is suppose to be delivered.
    destination_ip = ""
    # Destination mask.
    # Mask where our message or response is suppose to be delivered.
    destination_mask = 0
    # Destination port.
    # Port where our message or response is suppose to be delivered.
    destination_port = 0
    # Source IP.
    # IP where our message or response is suppose to be received.
    source_ip = ""
    # Source port.
    # Port where our message or response is suppose to be received.
    source_port = 0
    # Package size.
    # Can only be between 1 and 256 bytes.
    package_size = 0
    # Data.
    # Here we will add our message's data.
    data = ""

    # Message initializer.
    def __init__(self):
        pass

    # Return a new message object.
    @staticmethod
    def make_message():
        return MessagePseudoTCP()

    # Method that interprets the function of setting the flags in our message.
    # Also, it tell us if all the information added is correct.
    def set_flags(self, syn_flag, closure_flag, sn_flag, rn_flag, first_package_flag, last_package_flag):

        # Check that all the values encoded are really booleans.
        if (type(syn_flag) is type(True) and type(closure_flag) == type(True) and type(sn_flag) == type(True)
                and type(rn_flag) == type(True) and type(first_package_flag) == type(True)
                and type(last_package_flag) == type(True)):
            self.syn_flag = syn_flag
            self.closure_flag = closure_flag
            self.sn_flag = sn_flag
            self.rn_flag = rn_flag
            self.first_package_flag = first_package_flag
            self.last_package_flag = last_package_flag
            return True
        else:
            return False

    # Set our destination variables.
    def set_destination(self, destination_ip, destination_port, destination_mask):

        # Validate the port.
        try:
            num = int(destination_port)
        except ValueError:
            print("El puerto tiene quer ser una entrada númerica.")
            return False

        if num > 65535 or num < 1:
            print("El puerto tiene quer ser un número entre 256 y 1.")
            return False

        self.destination_port = destination_port

        # Validate the mask.
        try:
            num = int(destination_mask)
        except ValueError:
            print("La mascara tiene quer ser una entrada númerica.")
            return False

        if num > 256 or num < 0:
            print("La mascara tiene que ser un número entre 0 y 256.")
            return False

        self.destination_mask = destination_mask

        # Validate the ip address.
        try:
            ipaddress.ip_address(destination_ip)
        except ValueError as err:
            print("La dirección ip ingresada (%s) es erronear. Error: %s." %
                  (destination_ip, err))
            return False

        self.destination_ip = destination_ip

        return True

    # Set our source variables.
    def set_source(self, source_ip, source_port):

        # Validate the port.
        try:
            num = int(source_port)
        except ValueError:
            print("El puerto tiene quer ser una entrada númerica.")
            return False

        if num > 65535 or num < 1:
            print("El puerto tiene quer ser un número entre 65535 y 1.")
            return False

        self.source_port = source_port

        # Validate the ip address.
        try:
            ipaddress.ip_address(source_ip)
        except ValueError as err:
            print("La dirección ip ingresada (%s) es erronear. Error: %s." %
                  (source_ip, err))
            return False

        self.source_ip = source_ip

        return True

    def set_message(self, data, package_size):

        # Check that package size is actually a int.
        try:
            num = int(package_size)
        except ValueError:
            print("El tamaño del paquete tiene que ser un número entero.")
            return False

        # Check that package size is between 1 and 256.
        if not package_size >= 1 or not package_size <= 256:
            return False

        # Check if the length of the data is the same or less than package_size
        if len(data) > package_size or len(data) == 0:
            return False

        # Now, set our message.
        self.data = data
        self.package_size = package_size

    # Return a our message in a byte array.
    def encode_message(self):

        # Variable where we will save the size of our array.
        array_size = 0

        # Add the size of our header.
        # First we add 8 bytes. Two of them will be empty. The other six will hold our flags.
        array_size += 8
        # Now, we add 7 bytes, 4 for the destination ip, 2 for the destination port and 1 for the mask.
        array_size += 7
        # Lastly, we add 6 more, 4 for our source ip and 2 for our source port.
        array_size += 6

        # Now, we add one more byte for the size of the package.
        array_size += 1

        # Calculate the size of the message.
        if self.data != "":
            array_size += self.package_size

        # Create the byte array that we will be sending as a message.
        # Add our header.
        byte_array = bytearray(array_size)
        byte_array[0:1] = bytes(0)
        byte_array[1:2] = bytes(0)
        byte_array[2:3] = int(self.syn_flag).to_bytes(1, byteorder="big")
        byte_array[3:4] = int(self.closure_flag).to_bytes(1, byteorder="big")
        byte_array[4:5] = int(self.sn_flag).to_bytes(1, byteorder="big")
        byte_array[5:6] = int(self.rn_flag).to_bytes(1, byteorder="big")
        byte_array[6:7] = int(self.first_package_flag).to_bytes(1, byteorder="big")
        byte_array[7:8] = int(self.last_package_flag).to_bytes(1, byteorder="big")

        # Add our destination information.
        byte_array[8:12] = bytearray(bytes(map(int, self.destination_ip.split("."))))
        byte_array[12:13] = int(self.destination_mask).to_bytes(1, byteorder="big")
        byte_array[13:15] = int(self.destination_port).to_bytes(2, byteorder="big")

        # Add our source information.
        byte_array[15:19] = (bytearray(bytes(map(int, self.source_ip.split(".")))))
        byte_array[19:21] = (int(self.source_port).to_bytes(2, byteorder="big"))

        # Add our message.
        byte_array[21:22] =(int(self.package_size).to_bytes(1, byteorder="big"))
        if self.data != "":
            byte_array[22:22+self.package_size] = bytes(str.encode(self.data))

        # Return our byte_array.
        return byte_array

    # Check if we are trying to make a new connection.
    # To know if we are trying to make a new connection, we must have
    # the SYN flag set to true, all other flags set to false and the
    # data size must be 0.
    def check_new_connection_message(self):
        if (self.syn_flag is True and self.closure_flag is False
                and self.first_package_flag is False and self.last_package_flag is False
                and self.rn_flag is False and self.sn_flag is False
                and self.package_size == 0):
            return True
        else:
            return False

    # Check if a message is trying to make a new connection.
    # To know if a message is trying to make a new connection with our node, we must have
    # all flags set to false and the data size must be 0.
    def check_new_arriving_connection_message(self):
        if (self.syn_flag is False and self.closure_flag is False
                and self.first_package_flag is False and self.last_package_flag is False
                and self.rn_flag is False and self.sn_flag is False
                and self.package_size == 0):
            return True
        else:
            return False
