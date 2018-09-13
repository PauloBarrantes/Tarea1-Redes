from socket import *
serverPort = 8080
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("10.1.137.148", serverPort))
print ("The server is ready to receive")
while 1:
  message, clientAddress = serverSocket.recvfrom(2048)
  modifiedMessage = message.upper()
  print("El mensaje modificado:", modifiedMessage)
  serverSocket.sendto(modifiedMessage, clientAddress)
