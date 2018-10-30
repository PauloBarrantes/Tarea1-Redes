import threading


# Structure where we will save all the open connections.
# Note: Only one connection per host is allowed.
class PseudoTCPConnectionTable:

    # Create the instance of our table that will contain all the connections.
    def __init__(self):

        # This dictionary will contain a key, made by the ip destination and
        # the port destination and will have as value, the thread that is
        # maintaining the connection alive. Also, we will be adding a lock,
        # so that no more than one operation at a time can modify an entry.
        self.pseudo_tcp_connection_table = {}

    # Add a new connection to our table.
    def add_connection(self, ip_destination, port_destination, thread):

        # Check that the connection doesn't already exist.
        if self.search_connection(ip_destination, port_destination):
            print("La conexión con el nodo con dirección ", ip_destination,
                  " y puerto ", port_destination, " ya existe.")
            return False

        # Create a new lock for this entry.
        entry_lock = threading.Lock()

        # Add the new connection to the table.
        self.pseudo_tcp_connection_table.update({(ip_destination, port_destination):
                                                 [thread, entry_lock]})

    # Search for a connection.
    def search_connection(self, ip_destination, port_destination):

        # Fetch the entry.
        entry = self.pseudo_tcp_connection_table.get((ip_destination, port_destination))

        # If it doesn't exist, then return false.
        if entry:
            return entry
        else:
            return False

    # Close a connection.
    def close_connection(self, ip_destination, port_destination):

        # First, let's try to fetch the entry.
        entry = self.pseudo_tcp_connection_table.get((ip_destination, port_destination))

        if entry:

            # Get the lock, so that we won't lose it when deleting the row.
            # After fetching it, we just acquire it.
            entry_lock = entry[1]
            entry_lock.acquire()

            # Now pop the entry and tell the thread to finish.
            # We will be telling the thread it is done, by sending a -1.
            # After all, release the lock so that other connections can work.
            entry[0].thread_queue.put(-1)
            self.pseudo_tcp_connection_table.pop((ip_destination, port_destination))
            entry_lock.release()
        else:
            print("La conexión con el nodo con dirección ", ip_destination,
                  " y puerto ", port_destination, " no existe.")
