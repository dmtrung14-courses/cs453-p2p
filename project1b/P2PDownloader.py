import time
import random
import socket
import sys

def get_torrent_metadata(filename, tracker_ip, tracker_port):
    # Create a UDP socket
    

    # Send the torrent metadata request
    request = f"GET {filename}.torrent\n"
    

    peers = set()
    for i in range(3):
        print(f"Requesting for the {i+1} time")
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(request.encode(), (tracker_ip, tracker_port))
        # Receive the torrent metadata response
        response, _ = udp_socket.recvfrom(1024)
        
        metadata = response.decode().split('\n')

        # Parse the metadata
        num_blocks = int(metadata[0].split(': ')[1])
        file_size = int(metadata[1].split(': ')[1])
        
        for i in range(2, len(metadata)-1, 2):
            ip = metadata[i].split(': ')[1]
            port = int(metadata[i+1].split(': ')[1])
            peers.add((ip, port))

        # Close the UDP socket
        udp_socket.close()
        # Sleep for 2 second
        time.sleep(2)

    return num_blocks, file_size, list(peers)

def download_file(filename, num_blocks, peers):
    print("Downloading the file...")
    # Create a TCP socket for each peer
    print("Number of peers found: ", len(peers))
    print("Number of blocks: ", num_blocks)
    tcp_sockets = []
    for peer in peers:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(peer)
        tcp_sockets.append(tcp_socket)
    # Download each block from a random peer
    with open(filename, 'wb') as file:
        for block_number in range(num_blocks):
            # Choose a random peer
            peer_index = random.randint(0, len(peers)-1)
            peer_socket = tcp_sockets[peer_index]

            # Send the block request
            request = f"GET {filename}:{block_number}\n"
            peer_socket.send(request.encode())
            
            response = b""

            while True:
                try:
                    print(f"Response block: {block_number}  ", response)

                    response += peer_socket.recv(1024)
                    peer_socket.settimeout(0.5)
                except socket.timeout:
                    break
            # Receive the block response
            
            header_sep = response.index(b'\n\n')
            file.write(response[header_sep+2:])


    # Close all TCP sockets
    for tcp_socket in tcp_sockets:
        tcp_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python CSDownloader.py <filename> <address> <port>")
        sys.exit(1)

    filename = sys.argv[1]
    tracker_ip = sys.argv[2]
    tracker_port = int(sys.argv[3])

    # For quick testing prompt:
    # python P2PDownloader.py test.jpg date.cs.umass.edu 19876
    # python P2PDownloader.py redsox.jpg date.cs.umass.edu 19876

    num_blocks, file_size, peers = get_torrent_metadata(filename, tracker_ip, tracker_port)
    download_file(filename, num_blocks, peers)