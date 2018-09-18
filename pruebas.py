class Node:
    def __init__(self, protocolo, dirNodo, numeroPuerto):
        self.protocolo = protocolo
        self.direccionNodo = dirNodo
        self.puertoNodo = int(numeroPuerto)

    def __del__(self):
        print("Node was successfully deleted")

    def nodeMenu(self):
        ##Variables
        opcion = "0"
        ## Menu
        while opcion != "3":
            print("You are now working with node", self.direccionNodo + "!")
            print("What do you want to do?")
            print("1 - Enviar Mensaje ")
            print("2 - Borrar nodo ")
            print("3 - Salir")

            opcion = input("¿? \n")

            if(opcion ==  "1"):
                print("Usted quiere enviar un mensaje")
            if(opcion == "2"):
                print("Usted quiere eliminar este nodo")
                #envia mensaje con un 0 para que se borre de las tablas
                #del self
            if(opcion == "3"):
                print("Good bye!")


class NodeTCP(Node):

    def __init__(self, dirNodo,numeroPuerto):
        super().__init__("pseudoBGP", dirNodo, numeroPuerto)
        self.servidor = "soy un objeto servidor"


nodo = NodeTCP("1.1.1.1", "900")
print(nodo.protocolo, nodo.direccionNodo, nodo.puertoNodo, nodo.servidor)
nodo.nodeMenu()