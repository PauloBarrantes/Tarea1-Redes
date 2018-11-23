from texttable import *
import threading


class NeighborsTable:

    def __init__(self):
        self.neighbors = {}
    def is_awake(self, ip, port):
        return self.neighbors.get((ip, mask, port))[1]

    # Marcar despierto
    def mark_awake(slef, ip, port):
        self.neighbors.get((ip, port))[1] = True

    # Save the ip from the source of the message and the mask as the key. For the entry,
    # we will save the message ip address, the cost and the port it is working on.
    def save_address(self, ip, mask, port, cost, awake):

        # First, we need to make sure that we have the key in table.
        if self.neighbors.get((ip, port)):

            # If we did find the key, then we need to try to acquire the lock, before
            # updating the table, and make sure it is not in the process of being remove.
            # Also, we need to catch any lock exception, because in case the lock gets remove while updating the table.
            try:

                # Acquire the lock.
                lock = self.neighbors.get((ip, port))[2]
                lock.acquire()

                # Now update the table and release the lock when finished.
                if self.neighbors.get((ip, port))[0] > cost:
                    self.neighbors.update({(ip, port): [cost, awake,mask, lock]})
                    lock.release()

            except threading.ThreadError:

                # The lock got remove, so just keep going, we know we can't update it.
                print("No se pudo modificar la entrada: " + ip + ", " + mask + ", " + port + ". Intente de nuevo.")
                return

        else:

            # Create a new lock for this entry and a lock check, in case we are deleting it.
            entry_lock = threading.Lock()
            self.neighbors.update({(ip, port): [cost, awake, mask, entry_lock]})


    # Remove an entry from the reachability table.
    def remove_address(self, ip, port):

        for key in list(self.neighbors):
            if self.neighbors.get(key)[0] == ip and  and self.neighbors.get(key)[1] == port:
                # Acquire the lock, remove the entry and then release the lock.
                # In order to avoid any errors, we need to keep our lock in memory.
                entry_lock = self.neighbors.get(key)[3]
                entry_lock.acquire()
                self.neighbors.pop(key)
                entry_lock.release()

    # Print the reachability table.
    def print_table(self):
        print("TABLA DE VECINOS")
        table = Texttable()
        table.set_cols_align(["c","c","c","c","c"])
        table.set_cols_valign(["m","m","m","m","m"])
        table.add_row(["IP", "Máscara", "Puerto", "Costo", "Estado"])
        for key in self.neighbors:
            table.add_row([key[0], self.neighbors.get(key)[2], key[1], self.neighbors.get(key)[0], self.neighbors.get(key)[1]])

        print (table.draw() + "\n")
'''
vecinos = NeighborsTable()
vecinos.save_address("127.0.0.1", 16, 8080, 50)
vecinos.print_table()
'''
