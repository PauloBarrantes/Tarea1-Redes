class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self, arg):
        self.tabla = {}

    def agregarDireccion(self, ip, mascara, costo):
        self.tabla.update({ip+mascara:costo})

    def buscarDireccion (self, ip, mascara):
        result = self.tabla.get(ip)
        if result :
            return 1
        else:
            return 0

    def