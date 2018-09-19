from texttable import *

class ReachabilityTables():
    """docstring for ReachabilityTables."""
    def __init__(self):
        self.tabla = {}
    ## Guarda la dirección del mensaje, la ip del origen del mensaje, la máscara del mensaje y el costo
    def agregarDireccion(self, ip, origen, mascara, costo):
        if self.tabla.get(ip):
            if self.tabla.get(ip)[2] > costo:
                self.tabla.update({ip:[origen, mascara, costo]})
        else:
            self.tabla.update({ip:[origen, mascara, costo]})
    #Elimina una fila de la tabla donde coincida con la ip que entró
    def eliminarDireccion(self, ip):
        self.tabla.pop(ip)
    ##Imprime en formato de tabla la tabla de alcanzabilidad de un nodo
    def imprimirTabla(self):
        print("TABLA DE ALCANZABILIDAD")
        table = Texttable()
        table.set_cols_align(["l", "r", "c","k"])
        table.set_cols_valign(["t", "m", "b","a"])
        table.add_row(["IP", "Origen", "Máscara","Costo"])
        for key in self.tabla:
            table.add_row([key,self.tabla.get(key)[0],self.tabla.get(key)[1],self.tabla.get(key)[2]])

        print (table.draw() + "\n")
