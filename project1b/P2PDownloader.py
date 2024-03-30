import socket

def get_torrent_metadata(filename, tracker_ip, tracker_port):
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the torrent metadata request
    request = f"GET {filename}.torrent\n"
    udp_socket.sendto(request.encode(), (tracker_ip, tracker_port))

    # Receive the torrent metadata response
    response, _ = udp_socket.recvfrom(1024)
    metadata = response.decode().split('\n')

    # Parse the metadata
    num_blocks = int(metadata[0].split(': ')[1])
    file_size = int(metadata[1].split(': ')[1])
    peers = []
    for i in range(2, len(metadata), 2):
        ip = metadata[i].split(': ')[1]
        port = int(metadata[i+1].split(': ')[1])
        peers.append((ip, port))

    # Close the UDP socket
    udp_socket.close()

    return num_blocks, file_size, peers

def download_file(filename, num_blocks, file_size, peers):
    # Create a TCP socket for each peer
    tcp_sockets = []
    for peer in peers:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(peer)
        tcp_sockets.append(tcp_socket)

    # Download each block from a random peer
    with open(filename, 'wb') as file:
        for block_number in range(num_blocks):
            # Choose a random peer
            peer_index = random.randint(0, len(peers) - 1)
            peer_socket = tcp_sockets[peer_index]

            # Send the block request
            request = f"GET {filename}:{block_number}\n"
            peer_socket.send(request.encode())

            # Receive the block response
            response = peer_socket.recv(1024)
            response = response.decode().split('\n')

            # Parse the block response
            body_byte_offset = int(response[1].split(': ')[1])
            body_byte_length = int(response[2].split(': ')[1])
            body = response[4]

            # Write the block to the file
            file.seek(body_byte_offset)
            file.write(body.encode())

    # Close all TCP sockets
    for tcp_socket in tcp_sockets:
        tcp_socket.close()

# Usage example
filename = "redsox.jpg"
tracker_ip = "date.cs.umass.edu"
tracker_port = 19876

num_blocks, file_size, peers = get_torrent_metadata(filename, tracker_ip, tracker_port)
download_file(filename, num_blocks, file_size, peers)