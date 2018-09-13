from socket import *
serverPort = 8080
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('10.1.138.89',serverPort))
serverSocket.listen(10)
print ("The server is ready to receive")
while 1:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024)
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence)
    connectionSocket.close()
