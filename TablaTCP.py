

class TablaTCP():

    """docstring for TablaTCP."""
    def __init__(self):
        self.table = {}

    def save_connection(self, ip, port, connectionSocket):
        self.table.update({(ip,port): connectionSocket})

    def search_connection(self, ip, port):
        if self.table.get((ip,port)):
            return self.table.get((ip,port))
        return -1

    def close_connection(self, ip, port):
        if self.table.get((ip, port)):
            self.table.get((ip, port)).close()
            self.table.pop((ip, port))
    
#
# tablita = TablaTCP()
# tablita.guardarConexion('180.1.3.5',12412,"GG")
#
# gg = tablita.buscarConexion('180.1.3.5',4)
# print(gg)
#
# gg = tablita.buscarConexion('180.1.3.15',2 )
# print(gg)
