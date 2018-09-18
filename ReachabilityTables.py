class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self, arg):
        self.tabla = {'localhost':[1,24,100]}

    def agregarDireccion(self, ip, red, mascara, costo):
        self.tabla.update({ip:[red, mascara, costo]})
    def imprimirTabla(self):
        print(self.tabla)
    def buscarDireccion (self, ip):
        result = self.tabla.get(ip)
        if result :
            return 1
        else:
            return 0


#gg = ReachabilityTables()
