from socket import timeout, socket, AF_INET, SOCK_STREAM
import io
from PIL import Image
import sys

def download_image(filename, address, port):
    # Create a socket object
    client_socket = socket(AF_INET, SOCK_STREAM)
    # Define the server address and port
    server_address = (address, port)
    # Connect to the server
    client_socket.connect(server_address)
    # Send the request to download the file
    request = f"GET {filename}\n"
    client_socket.send(request.encode())
    # print("Connected to Server. Requesting file...")
    data = b""
    # Receive the response from the server
    while True:
        try:
            response = client_socket.recv(1024)
            data += response
            client_socket.settimeout(5)
        except timeout:
            break

    # print("Done getting files, preparing to save...")
    header_sep = data.index(b'\n\n')
    file = data[header_sep+2:]
    # # Create an image object from the bytes
    # image = Image.open(io.BytesIO(file))

    # # Save the image file
    # image.save(filename)

    with open(filename, 'wb') as f:
        f.write(file)

    client_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python CSDownloader.py <filename> <address> <port>")
        sys.exit(1)

    filename = sys.argv[1]
    address = sys.argv[2]
    port = int(sys.argv[3])

    download_image(filename, address, port)
