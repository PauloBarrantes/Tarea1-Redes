from socket import *
serverName = '10.1.138.89'
serverPort = 8080
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = str.encode(input("Input lowercase sentence:"))
clientSocket.send(sentence)
modifiedSentence = clientSocket.recv(1024)
print ("From Server:" , modifiedSentence)
clientSocket.close()