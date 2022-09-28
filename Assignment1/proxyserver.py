from socket import *

serverPort = 8888
serverSocket = socket(AF_INET, SOCK_STREAM)# Create TCP welcoming socket
serverSocket.bind(('', serverPort))

serverSocket.listen(1)# Server begins listening for incoming TCP requests
print('Starting Proxy Server')
while True:
    connectionSocket, addr = serverSocket.accept()# Server waits on accept() for incoming requests, new socket created on return
    try:
        message = connectionSocket.recv(1024).decode()# Read bytes from socket
        arrOfHeaders = message.split('\r\n')# HTTP message header lines in array
        filePath = arrOfHeaders[0].split()[1].split("/")# Array of the file path
        getFileName = filePath[len(filePath)-1]# File name with file extension
        getDomain = arrOfHeaders[0].split('/')[1]# The domain of the server

        try:
            # Looking through proxy server cache
            print("Looking through cache for file")
            fileType = getFileName.split('.')[1]# Note down file extension
            connectionSocket.send('HTTP/1.1 200 OK\r\n'.encode())# Send Back HTTP status code
            if getFileName != 'favicon.ico':# Make sure favicon.ico is not the target file 
                if fileType == 'html': # file extension matches html
                    targetFile = open(getFileName)
                    fileContent = targetFile.read()
                    connectionSocket.send('Content-Type: text/html\n\n'.encode())
                    for i in range(0, len(fileContent)):
                        connectionSocket.send(fileContent[i].encode())
                        targetFile.close()
                if fileType == 'png' or fileType == 'jpg' or fileType == 'jpeg':# file extension matches png, jpg, jpeg
                    targetFile = open(getFileName, 'r+b')# Open the binary file in read or write mode
                    fileContent = targetFile.read()# Read content of file
                    connectionSocket.send('Content-Type: image/jpeg\r\n'.encode())# Add header line so Image can be formated correctly
                    sizeOfImage = bytes('Content-Length: ' + str(len(fileContent)) + '\r\n' , 'utf8')# Allocate space for Content Length
                    connectionSocket.send(sizeOfImage)
                    connectionSocket.send('\r\n'.encode())
                    connectionSocket.send(fileContent)
                    targetFile.close()
            connectionSocket.close()
        except:
            # Getting file from the server
            print("Getting file from server")
            try:
                if getFileName == 'favicon.ico':#If fvicon.ico is receieved, close connection
                    connectionSocket.close()
                else:
                    clientSocket = socket(AF_INET, SOCK_STREAM)#Ceate TCP socket for server
                    clientSocket.connect((gethostbyname(getDomain), 80))#Connect to the server through port 80
                    newHeader = message.replace("/" + getDomain, "")#Alter header to send request
                    clientSocket.send(newHeader.encode())#Send Request to server
                    fileContent = open(getFileName, 'w')#Open file to Write
                    while True:
                        anotherMessage = clientSocket.recv(1024)# Read bytes from socket
                        # Parsing content to save to cache
                        parseMessage = anotherMessage.decode().split('\r\n')
                        filterMessage = parseMessage[len(parseMessage) - 1]
                        fileContent.write(filterMessage)
                        connectionSocket.send(anotherMessage)
                        if(anotherMessage == b''):#Break when receiving empty message
                            break
                    fileContent.close()
                    clientSocket.close()
                    connectionSocket.close()
            except:
                # Send Back 404 HTTP status code
                connectionSocket.send('\nHTTP/1.1 404 Not Found\r\n\r\n'.encode())
                # Close socket
                connectionSocket.close()
    except:
        connectionSocket.close()