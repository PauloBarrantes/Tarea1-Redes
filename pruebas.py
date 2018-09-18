class Node:
    def __init__(self, protocolo, dirNodo, numeroPuerto):
        self.protocolo = protocolo
        self.direccionNodo = dirNodo
        self.puertoNodo = int(numeroPuerto)

    def __del__(self):
        print("Node was successfully deleted")


class NodeTCP(Node):

    def __init__(self, dirNodo,numeroPuerto):
        super().__init__("pseudoBGP", dirNodo, numeroPuerto)
        self.servidor = "soy un objeto servidor"


nodo = NodeTCP("1.1.1.1", "900")
print(nodo.protocolo, nodo.direccionNodo, nodo.puertoNodo, nodo.servidor)