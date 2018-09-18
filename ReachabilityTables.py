from texttable import *

class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self):
        self.tabla = {'localhost':[1,24,100]}

    def agregarDireccion(self, ip, red, mascara, costo):
        self.tabla.update({ip:[red, mascara, costo]})
    def imprimirTabla(self):
        print("TABLA DE ALCANZABILIDAD")
        table = Texttable()
        table.set_cols_align(["l", "r", "c","k"])
        table.set_cols_valign(["t", "m", "b","a"])
        table.add_rows([
                        ["IP", "Red", "Máscara","Costo"],
                        for key in self.tabla:
                            [value.key]
                            ["GG", 32, "Xav'",334],
                            ["GG", 32, "Xav'",334],
                            ["GG", 2, "F'",1]])
        print (table.draw() + "\n")

    def buscarDireccion (self, ip):
        result = self.tabla.get(ip)
        if result :
            return 1
        else:
            return 0


gg = ReachabilityTables()
gg.imprimirTabla()
gg.agregarDireccion("172.18.190.1",3,4,599)
gg.imprimirTabla()

dir = gg.buscarDireccion("localhost")
print(dir)
