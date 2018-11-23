from threading import Thread
from queue import Queue
from socket import *
from pseduotcp import PseudoTCPConnectionTable
from pseduotcp import MessagePseudoTCP
import os
import time
import sys, traceback


# Class that will maintain the connection with another node.
# This class will work as a thread.
class PseudoTCPThread(Thread):

    # This is a queue that will be maneging our thread behavior.
    thread_queue = Queue()
    # Table with all current connections in our node.
    pseudo_tcp_connection_table: PseudoTCPConnectionTable

    # Init our thread class.
    def __init__(self, pseudo_tcp_connection_table, destination_ip, destination_mask, destination_port,
                 source_ip, source_port, file_name):
        Thread.__init__(self)
        self.pseudo_tcp_connection_table = pseudo_tcp_connection_table
        # Set our destination variables.
        self.destination_ip = destination_ip
        self.destination_mask = destination_mask
        self.destination_port = destination_port
        # Set our source variables.
        self.source_ip = source_ip
        self.source_port = source_port
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        # This variable will let us know what was the last value of our sn flag.
        self.thread_sn_flag = False
        # This variable will let us know what was the last value of our rn flag.
        self.thread_rn_flag = False
        # This variable will hold how many times in a row, we received a wrong message.
        # We will use it to get out of the while loop if we received to many wrong messages.
        self.counter_error = 0
        self.file_name = file_name
        self.file = ""
        self.file_to_write = ""
        # Count in what position we are at.
        self.file_counter = 0
        # Number of bytes read per message.
        self.file_bytes_read = 20
        self.duplex = False

    # Method that will be executed asynchronously.
    def run(self):

        # Our first step, is to wait for a message.
        try:

            # Flag that will tell us that we are finished.
            finish_flag = False

            # Variable where we will save our last message, in case
            # we need to a retransmission.
            last_message = ""

            # Of course, while our flag is not True, then we must continue.
            while not finish_flag or self.counter_error > 5:

                # Wait for a message during 10 seconds.
                # If after 10 seconds, nothing is received, then we finish our thread.
                message = self.thread_queue.get(True, 10)

                # First, let's check that we are not being told to stop.
                # If we are being told to stop, the message received will be -1.
                # We need to set the finish flag to True and then break from the
                # current while iteration. We could of use break instead, but
                # it is always better to avoid breaking from iterations.
                if message == -1:
                    finish_flag = True
                    # Close the connection with our client.
                    self.client_socket.close()
                    self.thread_queue.task_done()
                    continue

                # Now, let's check if we can cast our message to a pseudo tcp message
                # object and check if we are trying to do a new connection.
                message: MessagePseudoTCP
                if message.check_new_connection_message():

                    try:
                        self.connect(message)

                        # After a successful connection, we need to move to the next
                        # while iteration.
                        self.thread_queue.task_done()
                        continue
                    except Exception:

                        # Error trying to connect.
                        print("No pudimos concreatar la conexión.")

                        # Close the connection and tell our queue we finished.
                        finish_flag = True
                        self.pseudo_tcp_connection_table.close_connection(self.destination_ip, self.destination_port)
                        self.client_socket.close()
                        self.thread_queue.task_done()
                        continue

                # Now we will check if someone wants to do a new connection with us.
                # This means all flags will be false and the package size will be 0.
                if message.check_new_arriving_connection_message():

                    if self.duplex is True:
                        self.file.close()

                    self.accept(message)

                    # After a successful accept, we need to move to the next
                    # while iteration.
                    self.thread_queue.task_done()
                    continue

                # Now, from here on, this is where we will be sending and
                # receiving messages with payloads. We initiate this process
                # when we receive the first ACK. This ACk will have our sn_flag
                # inverted, but also will have the SYN, first and last flag toggle.
                if (message.syn_flag is True and self.thread_sn_flag is not message.rn_flag
                        and message.first_package_flag is True and message.last_package_flag is True):

                    if self.duplex is False: print('El handshake se realizo con éxito entre los nodos.')
                    self.duplex = True

                    # Change our SN to the new SN value.
                    self.thread_sn_flag = message.rn_flag

                    # Get our file and read it.
                    cwd = os.getcwd()
                    file_path = cwd + "/" + self.file_name
                    # Open the file.
                    self.file = open(file_path)
                    package_message = self.file.read(20)
                    closure_flag = False
                    last_package = False

                    if len(package_message) < self.file_bytes_read:
                        closure_flag = True
                        last_package = True

                    # Now we set up our new message.
                    message_data = MessagePseudoTCP.MessagePseudoTCP()
                    message_data.set_flags(False, closure_flag, self.thread_sn_flag, message.sn_flag,
                                           True, last_package)
                    message_data.set_destination(self.destination_ip, self.destination_port, self.destination_mask)
                    message_data.set_source(self.source_ip, self.source_port)
                    message_data.set_message(package_message, len(package_message))
                    last_message = message_data
                    self.client_socket.send(message_data.encode_message())
                    self.thread_queue.task_done()
                    continue

                # If we are receiving the first package.
                if (message.first_package_flag is True and message.sn_flag is self.thread_rn_flag
                        and message.package_size > 0):

                    # Get our file and write on it.
                    cwd = os.getcwd()
                    file_to_write_name = self.source_ip.replace(".", "") + str(self.source_port) + ".txt"
                    file_to_write_path = cwd + "/" + file_to_write_name
                    self.file_to_write = open(file_to_write_path, "a")
                    self.file_to_write.write(message.data)

                    self.thread_rn_flag = not message.sn_flag

                    # Set up our message.
                    message_data = MessagePseudoTCP.MessagePseudoTCP()
                    message_data.set_flags(False, False, message.sn_flag, not message.sn_flag,
                                           False, False)
                    message_data.set_destination(self.destination_ip, self.destination_port, self.destination_mask)
                    message_data.set_source(self.source_ip, self.source_port)
                    message_data.set_message("", 0)
                    last_message = message_data
                    self.client_socket.send(message_data.encode_message())
                    continue

                # If we are receiving a middle package.
                if (message.first_package_flag is False and message.sn_flag is self.thread_rn_flag
                        and message.package_size > 0 and message.last_package_flag is False):

                    # Get our file and write on it.
                    self.file_to_write.write(message.data)

                    self.thread_rn_flag = not message.sn_flag

                    # Set up our message.
                    message_data = MessagePseudoTCP.MessagePseudoTCP()
                    message_data.set_flags(False, False, message.sn_flag, not message.sn_flag,
                                           False, False)
                    message_data.set_destination(self.destination_ip, self.destination_port, self.destination_mask)
                    message_data.set_source(self.source_ip, self.source_port)
                    message_data.set_message("", 0)
                    last_message = message_data
                    self.client_socket.send(message_data.encode_message())
                    continue

                # If we are receiving the last package.
                if (message.first_package_flag is False and message.sn_flag is self.thread_rn_flag
                        and message.package_size > 0 and message.last_package_flag is True):
                    # Get our file and write on it.
                    self.file_to_write.write(message.data)

                    self.thread_rn_flag = not message.sn_flag

                    # Set up our message.
                    message_data = MessagePseudoTCP.MessagePseudoTCP()
                    message_data.set_flags(False, True, message.sn_flag, not message.sn_flag,
                                           False, False)
                    message_data.set_destination(self.destination_ip, self.destination_port, self.destination_mask)
                    message_data.set_source(self.source_ip, self.source_port)
                    message_data.set_message("", 0)

                    if self.duplex is False:

                        # Set duplex to true.
                        self.duplex = True

                        # Set the new message.
                        # The ACK will have the SN flag and the SYN flag toggled.
                        connection_message = MessagePseudoTCP.MessagePseudoTCP()
                        connection_message.set_flags(False, False, False,
                                                     False, False, False)
                        connection_message.set_destination(message.destination_ip, message.destination_port,
                                                           message.destination_mask)
                        connection_message.set_source(self.source_ip, self.source_port)

                        # Send the message.
                        self.client_socket.send(connection_message.encode_message())
                        continue

                    self.client_socket.send(message_data.encode_message())
                    time.sleep(1)

                    self.pseudo_tcp_connection_table.close_connection(self.destination_ip, self.destination_port)
                    self.client_socket.close()
                    finish_flag = True
                    continue

                # If we get the correct rn and doesn't have data.
                # If so, then we send the next chuck of data.
                if (message.rn_flag is not self.thread_sn_flag and message.package_size == 0
                        and message.closure_flag is not True):

                    self.thread_sn_flag = message.rn_flag

                    package_message = self.file.read(20)
                    closure_flag = False
                    last_package = False

                    if len(package_message) < self.file_bytes_read:
                        closure_flag = True
                        last_package = True

                    # Now we set up our new message.
                    message_data = MessagePseudoTCP.MessagePseudoTCP()
                    message_data.set_flags(False, closure_flag, self.thread_sn_flag, self.thread_rn_flag,
                                           False, last_package)
                    message_data.set_destination(self.destination_ip, self.destination_port, self.destination_mask)
                    message_data.set_source(self.source_ip, self.source_port)
                    message_data.set_message(package_message, len(package_message))
                    last_message = message_data
                    self.client_socket.send(message_data.encode_message())
                    self.thread_queue.task_done()
                    continue

                # Check if this was the last message. If so, then we are over and don't need to
                # receive anymore packages.
                if message.closure_flag is True:

                    self.pseudo_tcp_connection_table.close_connection(self.destination_ip, self.destination_port)
                    self.client_socket.close()
                    finish_flag = True
                    continue

                # If none of the messages are satisfactory, then we resend our last message.
                print("Retransmitiendo el ultimo paquete.")
                self.client_socket.send(last_message.encode_message())

                # Tell our thread, this one task is done and I am ready to the the next one.
                # This must always be called at the end of each queue operation.
                self.thread_queue.task_done()

            # End of while.
            print("La transferencia del archivo se realizo con éxito.")
            print("Cerrando la conexión con el nodo.")

        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** print_tb:")
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            print("*** print_exception:")
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            print("*** print_exc:")
            traceback.print_exc()

            # Handle any issue with our queue not getting a message
            # in the given timeout. Also, delete this thread from the
            # connection table.
            print("Error, nuestra conexión se ha cerrado, pues no se recibio ningun mensaje durante 10 segundos.")
            self.pseudo_tcp_connection_table.close_connection(self.destination_ip, self.destination_port)
            self.client_socket.close()

    # Function that will simulate TCP connect.
    def connect(self, message):

        # First, let's add the thread to our pseudo tcp connection table.
        # The key will be the destination variables.
        self.pseudo_tcp_connection_table.add_connection(message.destination_ip, message.destination_port, self)

        # Set the new message.
        # The ACK will have the SN flag and the SYN flag toggled.
        connection_message = MessagePseudoTCP.MessagePseudoTCP()
        connection_message.set_flags(False, False, False,
                                     False, False, False)
        connection_message.set_destination(message.destination_ip, message.destination_port, message.destination_mask)
        connection_message.set_source(self.source_ip, self.source_port)

        # Try sending a message to the destination node.
        print("Estableciendo comunicación con el node con dirección ",
              connection_message.destination_ip, " y puerto ", connection_message.destination_port)
        self.client_socket.connect((str(connection_message.destination_ip), connection_message.destination_port))
        self.client_socket.send(connection_message.encode_message())

    # Function that will simulate TCP accept.
    def accept(self, message):

        # First, we need to add the connection.
        # They key in this case is the message's source variables.
        # That is because that's where we are sending our responses.
        self.pseudo_tcp_connection_table.add_connection(message.source_ip, message.source_port, self)

        print("Reciviendo nueva conexión del node con dirección ", message.source_ip,
              " con puerto ", message.source_port)
        print("Enviando ACK.")

        # Set the new message.
        # The ACK will have the RN flag, the SYN, the first package and last package flag toggled.
        ack_message = MessagePseudoTCP.MessagePseudoTCP()
        ack_message.set_flags(True, False, message.sn_flag,
                              not message.sn_flag, True, True)
        ack_message.set_destination(message.source_ip, message.source_port, "32")
        ack_message.set_source(self.source_ip, self.source_port)
        self.thread_rn_flag = not message.sn_flag

        # Send the message.
        self.client_socket.connect((str(ack_message.destination_ip), ack_message.destination_port))
        self.client_socket.send(ack_message.encode_message())
