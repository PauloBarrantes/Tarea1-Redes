from texttable import *
import threading


class ReachabilityTables:

    """docstring for ReachabilityTables."""
    def __init__(self):
        self.reach_table = {}

    # Save the ip from the source of the message and the mask as the key. For the entry,
    # we will save the message ip address, the cost and the port it is working on.
    def save_address(self, destination_ip, destination_mask, destination_port, cost, pivot_ip, pivot_mask, pivot_port):
        # First, we need to make sure that we have the key in table.
        if self.reach_table.get((destination_ip, destination_port)):

            # If we did find the key, then we need to try to acquire the lock, before
            # updating the table, and make sure it is not in the process of being remove.
            # Also, we need to catch any lock exception, because in case the lock gets remove while updating the table.
            try:

                # Acquire the lock.
                lock = self.reach_table.get((destination_ip, destination_port))[4]
                lock.acquire()

                # Now update the table and release the lock when finished.
                updateCost = cost + self.reach_table.get((pivot_ip, pivot_port))[0]

                if self.reach_table.get((destination_ip, destination_port))[0] > updateCost:

                    self.reach_table.update({(destination_ip, destination_port): [updateCost, pivot_ip, pivot_mask, pivot_port, lock, destination_mask]})

                lock.release()

            except threading.ThreadError:

                # The lock got remove, so just keep going, we know we can't update it.
                print("No se pudo modificar la entrada: " + destination_ip + ", " + destination_mask + ", " + destination_port + ". Intente de nuevo.")
                return

        else:

            # Create a new lock for this entry and a lock check, in case we are deleting it.
            entry_lock = threading.Lock()
            self.reach_table.update({(destination_ip, destination_port): [cost, pivot_ip, pivot_mask, pivot_port, entry_lock, destination_mask]})

    # Remove an entry from the reachability table.
    def remove_address(self, ip, mask, port):

        for key in list(self.reach_table):
            if self.reach_table.get(key)[0] == ip and  self.reach_table.get(key)[1] == port:
                # Acquire the lock, remove the entry and then release the lock.
                # In order to avoid any errors, we need to keep our lock in memory.
                entry_lock = self.reach_table.get(key)[4]
                entry_lock.acquire()
                self.reach_table.pop(key)
                entry_lock.release()


    def getPivots(self, ip, port):

        ip_pivot = self.reach_table.get((ip,port))[1]
        port_pivot = self.reach_table.get((ip,port))[3]
        pivots = (ip_pivot, port_pivot)

        return pivots
    # Print the reachability table.
    def print_table(self):
        print("TABLA DE ALCANZABILIDAD")
        table = Texttable()
        table.set_cols_align(["c","c","c","c","c","c","c"])
        table.set_cols_valign(["m","m","m","m","m","m","m"])
        table.add_row(["IP","Máscara","Puerto","Costo","IP Pivote","Máscara Pivote","Puerto Pivote"])
        for key in self.reach_table:
            table.add_row([key[0],  self.reach_table.get(key)[5], key[1], self.reach_table.get(key)[0],
                           self.reach_table.get(key)[1], self.reach_table.get(key)[2],
                            self.reach_table.get(key)[3]])

        print (table.draw() + "\n")

'''
alca = ReachabilityTables()
alca.save_address("127.0.0.1", 16, 8080, 50, "127.0.0.1", 16, 8081)
alca.print_table()
'''
