import threading


class LogWriter:

    def __init__(self, ip, port):
        # Change this address for one found in your computer.
        # File name.
        self.file_name = "node"+str(port)+".txt"
        # Log use to add safeguard our critical section.
        self.log_lock = threading.Lock()

    # Write to our node log.
    def write_log(self, message, mode):

        # First, let's acquire our lock.
        self.log_lock.acquire()

        # Now, create or open the log.
        file_object = open(self.file_name, "a+")

        # We can write to it now.
        if mode == 1:
            file_object.write("Message: %s | Type: Update. \n" % message)
        elif mode == 2:
            file_object.write("Message: %s | Type: KeepAlive. \n" % message)
        elif mode == 3:
            file_object.write("Message: %s | Type: ACK KeepAlive. \n" % message)
        elif mode == 4:
            file_object.write("Message: %s | Type: Flush. \n" % message)
        elif mode == 5:
            file_object.write("Message: %s | Type: Data. \n" % message)
        elif mode == 6:
            file_object.write("Message: %s | Type: Cost Change. \n" % message)
        elif mode == 7:
            file_object.write("Message: %s | Type: Dead. \n" % message)
        else:
            file_object.write("Message: %s | Type: Other. \n" % message)

        # Finally, realease the lock and close the file.
        file_object.close()
        self.log_lock.release()
