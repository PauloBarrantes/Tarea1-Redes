class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self, arg):
        self.tabla = {}

    def agregarDireccion(self, ip, red, mascara, costo):
        self.tabla.update({ip: costo})

    def buscarDireccion (self, ip):
        result = self.tabla.get(ip)
        if result :
            return 1
        else:
            return 0
