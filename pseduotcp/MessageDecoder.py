from .MessagePseudoTCP import *


# Object that will decode our message from a received bytes array.
class MessageDecoder:

    # Given a bytes array, decode the message a return a new pseudo tcp message.
    @staticmethod
    def decode_message(bytes_array):

        # Variable where we will save our message.
        message = MessagePseudoTCP()

        # Remember, the first two bytes are always empty.
        # First, we decode the flags.
        message.set_flags(
            # SYN flag.
            bool(int.from_bytes(bytes_array[2:3], byteorder="big")),
            # Closure flag.
            bool(int.from_bytes(bytes_array[3:4], byteorder="big")),
            # SN flag.
            bool(int.from_bytes(bytes_array[4:5], byteorder="big")),
            # RN flag.
            bool(int.from_bytes(bytes_array[5:6], byteorder="big")),
            # First package flag.
            bool(int.from_bytes(bytes_array[6:7], byteorder="big")),
            # Last package flag.
            bool(int.from_bytes(bytes_array[7:8], byteorder="big")))

        # Now, let's decode the destination.
        ip_list = list(bytes_array[8:12])
        destination_ip = ""
        for counter in range(0, len(ip_list)):
            if counter == len(ip_list)-1:
                destination_ip += str(ip_list[counter])
            else:
                destination_ip += str(ip_list[counter])
                destination_ip += "."
        destination_mask = int.from_bytes(bytes_array[12:13], byteorder="big")
        destination_port = int.from_bytes(bytes_array[13:15], byteorder="big")
        message.set_destination(destination_ip, destination_port, destination_mask)

        # Now, let's decode our source.
        ip_list = list(bytes_array[15:19])
        source_ip = ""
        for counter in range(0, len(ip_list)):
            if counter == len(ip_list) - 1:
                source_ip += str(ip_list[counter])
            else:
                source_ip += str(ip_list[counter])
                source_ip += "."
        source_port = int.from_bytes(bytes_array[19:21], byteorder="big")
        message.set_source(source_ip, source_port)

        # Data size and the payload.
        package_size = int.from_bytes(bytes_array[21:22], byteorder="big")
        payload = bytes_array[22: 22+package_size].decode("utf-8")
        message.set_message(payload, package_size)

        return message
