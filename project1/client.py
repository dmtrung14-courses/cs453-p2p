from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from socket import error

# Create a socket object
client_socket = socket(AF_INET, SOCK_STREAM)

# Define the server address and port
server_address = ('pear.cs.umass.edu', 18765)

# Connect to the server
client_socket.connect(server_address)

# Send the request to download the file
filename = 'test.jpg'  # Replace with the actual filename
request = f"GET {filename}\n"
client_socket.send(request.encode())

# Receive the response from the server
while True:
    response = client_socket.recv(1024)
    if not response:
        print("File not found on the server")
        break
    print(response, end='')


# Close the socket
client_socket.close()

