from SocketPseudoTCP import *


serverPort = int(input("Ingrese el puerto del servidor: "))
serverSocket = SocketPseudoTCP()
serverSocket.bind("localhost",serverPort)
serverSocket.listen(1)
print("Server listo para recibir mensajes")
while(1):
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024)
    print(str(addr))
    print(str(sentence))
    response = sentence.upper()
    connection.send(capitalizedSentences)
    connectionSocket.close()
