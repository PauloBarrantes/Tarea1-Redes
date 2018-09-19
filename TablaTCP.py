

class TablaTCP():
    """docstring for TablaTCP."""
    def __init__(self):
        self.table = {}

    def guardarConexion(self,ip,port,connectionSocket):
        self.table.update({ip:connectionSocket})
    def buscarConexion(self,ip, port):
        if self.table.get(ip):
            return self.table.get(ip)
        return -1


tablita = TablaTCP()
tablita.guardarConexion('180.1.3.5',12412,"GG")

gg = tablita.buscarConexion('180.1.3.5',4)
print(gg)

gg = tablita.buscarConexion('180.1.3.15',2 )
print(gg)
