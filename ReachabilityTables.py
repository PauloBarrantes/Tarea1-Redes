from texttable import *
import threading


class ReachabilityTables:

    """docstring for ReachabilityTables."""
    def __init__(self):
        self.reach_table = {}

    # Save the ip from the source of the message and the mask as the key. For the entry,
    # we will save the message ip address, the cost and the port it is working on.
    def save_address(self, ip, origin, mask, cost, port):

        # First, we need to make sure that we have the key in table.
        if self.reach_table.get((ip, mask)):

            # If we did find the key, then we need to try to acquire the lock, before
            # updating the table, and make sure it is not in the process of being remove.
            # Also, we need to catch any lock exception, because in case the lock gets remove while updating the table.
            try:

                # Acquire the lock.
                lock = self.reach_table.get((ip, mask))[3]
                lock.acquire()

                # Now update the table and release the lock when finished.
                if self.reach_table.get((ip, mask))[2] > cost:
                    self.reach_table.update({(ip, mask): [origin, port, cost, lock]})
                    lock.release()

            except threading.ThreadError:

                # The lock got remove, so just keep going, we know we can't update it.
                print("No se pudo modificar la entrada: " + ip + ", " + mask + ". Intente de nuevo.")
                return

        else:

            # Create a new lock for this entry and a lock check, in case we are deleting it.
            entry_lock = threading.Lock()
            self.reach_table.update({(ip, mask): [origin, port, cost, entry_lock]})

    # Remove an entry from the reachability table.
    def remove_address(self, ip, port):

        for key in self.reach_table:
            if self.reach_table.get(key)[0] == ip and self.reach_table.get(key)[1] == port:
                # Acquire the lock, remove the entry and then release the lock.
                # In order to avoid any errors, we need to keep our lock in memory.
                entry_lock = self.reach_table.get(key)[3]
                entry_lock.acquire()
                self.reach_table.pop(key)
                entry_lock.release()

    # Print the reachability table.
    def print_table(self):
        print("TABLA DE ALCANZABILIDAD")
        table = Texttable()
        table.set_cols_align(["l", "r","g" ,"c","k"])
        table.set_cols_valign(["t", "m","w", "b","a"])
        table.add_row(["IP", "Máscara", "Origen","Puerto","Costo"])
        for key in self.reach_table:
            table.add_row([key[0], key[1], self.reach_table.get(key)[0],
                           self.reach_table.get(key)[1], self.reach_table.get(key)[2]])

        print (table.draw() + "\n")
