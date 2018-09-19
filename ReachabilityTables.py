from texttable import *

class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self):
        self.tabla = {}

    def agregarDireccion(self, ip, origen, mascara, costo):
        if self.tabla.get(ip):
            print("Hay algo")
            if self.tabla.get(ip)[2] > costo:
                self.tabla.update({ip:[origen, mascara, costo]})
            else:
                print("No es menor")
        else:
            self.tabla.update({ip:[origen, mascara, costo]})
    def eliminarDireccion(self, ip):
        self.tabla.pop(ip)

    def imprimirTabla(self):
        print("TABLA DE ALCANZABILIDAD")
        table = Texttable()
        table.set_cols_align(["l", "r", "c","k"])
        table.set_cols_valign(["t", "m", "b","a"])
        table.add_row(["IP", "Origen", "Máscara","Costo"])
        for key in self.tabla:
            table.add_row([key,self.tabla.get(key)[0],self.tabla.get(key)[1],self.tabla.get(key)[2]])

        print (table.draw() + "\n")
