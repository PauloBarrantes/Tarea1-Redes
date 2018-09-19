from texttable import *

class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self):
        self.tabla = {}

    def agregarDireccion(self, ip, red, mascara, costo):
        self.tabla.update({ip:[red, mascara, costo]})
    def imprimirTabla(self):
        print("TABLA DE ALCANZABILIDAD")
        table = Texttable()
        table.set_cols_align(["l", "r", "c","k"])
        table.set_cols_valign(["t", "m", "b","a"])
        table.add_row(["IP", "Red", "Máscara","Costo"])
        for key in self.tabla:
            table.add_row([key,self.tabla.get(key)[0],self.tabla.get(key)[1],self.tabla.get(key)[2]])

        print (table.draw() + "\n")

    def buscarDireccion (self, ip):
        result = self.tabla.get(ip)
        if result :
            return 1
        else:
            return 0
