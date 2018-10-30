import threading


class LogWriter:

    def __init__(self):
        # Change this address for one found in your computer.
        self.dir_address = "/Users/alaincruzcasanova/PycharmProjects/Tarea1-Redes/"
        # File name.
        self.file_name = "node_log.txt"
        # Log use to add safeguard our critical section.
        self.log_lock = threading.Lock()

    # Write to our node log.
    def write_log(self, message, mode):

        # First, let's acquire our lock.
        self.log_lock.acquire()

        # Now, create or open the log.
        file_object = open(self.dir_address + self.file_name, "a+")

        # We can write to it now.
        if mode == 1:
            file_object.write("Message: %s | Type: Receiving. \n" % message)
        else:
            file_object.write("Message: %s | Type: Sending. \n" % message)

        # Finally, realease the lock and close the file.
        file_object.close()
        self.log_lock.release()
