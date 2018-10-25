from SocketPseudoTCP import *

while(1):
    serverIp = str(input("Ingrese un ip: "))
    serverPort = str(input("Ingrese un puerto: "))
    clientSocket = SocketPseudoTCP()
    clientSocket.connect((serverIp,serverPort))
    sentence = input("Mensaje: ")
    clientSocket.send(sentence.encode('utf-8'))
    response = clientSocket.recv(1024)
    print("Desde el servidor : "  + response.decode('utf-8'))
    clientSocket.close()
    break
