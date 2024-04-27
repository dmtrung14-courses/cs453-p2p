import socket
import sys

def send_message(server_address, server_port, message):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send the message to the server
        sock.sendto(message.encode(), (server_address, server_port))

        # Receive the response from the server
        data, server = sock.recvfrom(2048)
        response = data.decode()

        # Print the response
        print(response)

    finally:
        # Close the socket
        sock.close()

if __name__ == "__main__":
    # Parse command-line arguments
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    message = sys.argv[3]

    # Send the message to the server
    send_message(server_address, server_port, message)