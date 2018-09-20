

class TablaTCP():
    """docstring for TablaTCP."""
    def __init__(self):
        self.table = {}

    def guardarConexion(self,ip,port,connectionSocket):
        self.table.update({(ip,port):connectionSocket})
    def buscarConexion(self,ip, port):
        if self.table.get((ip,port)):
            return self.table.get((ip,port))
        return -1
    def eliminarConexion(self,ip, port):
        if self.table.get((ip,port)):
            self.table.get((ip,port)).close()
            self.tabla.pop((ip,port))
    
#
# tablita = TablaTCP()
# tablita.guardarConexion('180.1.3.5',12412,"GG")
#
# gg = tablita.buscarConexion('180.1.3.5',4)
# print(gg)
#
# gg = tablita.buscarConexion('180.1.3.15',2 )
# print(gg)
