from socket import *
# Port Number
serverPort = 6789
# Create TCP welcoming socket
serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(('', serverPort))
# Server begins listening for incoming TCP requests
serverSocket.listen(1)

while True:
    print('Server Started')
    # Server waits on accept() for incoming requests, new socket created on return
    connectionSocket, addr = serverSocket.accept()
    try:
        # Read bytes from socket
        message = connectionSocket.recv(1024).decode()
        # Parse the message for filename without /
        arrOfHeaders = message.split('\r\n')
        getFileName = arrOfHeaders[0].split()[1][1:]
        # Open file by name 
        targetFile = open(getFileName)
        # Read content of file
        fileContent = targetFile.read()
        # Send Back HTTP status code
        connectionSocket.send('HTTP/1.1 200 OK\r\n'.encode())
        # Add header line so HTML can be formated correctly
        connectionSocket.send('Content-Type: text/html\n\n'.encode())
        # Loop through file content and send data
        for i in range(0, len(fileContent)):
            connectionSocket.send(fileContent[i].encode())
        # End of data
        connectionSocket.send('\r\n\r\n'.encode())
        # Close socket
        connectionSocket.close()

    except:
        # Send Back 404 HTTP status code
        connectionSocket.send('\nHTTP/1.1 404 Not Found\r\n\r\n'.encode())
        # Close socket
        connectionSocket.close()