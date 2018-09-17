from socket import *
serverName = "10.1.138.89"
serverPort = 8080
clientSocket = socket(socket.AF_INET, socket.SOCK_DGRAM)
message = input("Input lowercase sentence:")
clientSocket.sendto(message,(serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print (modifiedMessage)
clientSocket.close()