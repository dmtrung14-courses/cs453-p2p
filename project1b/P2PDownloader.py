import time
import random
import socket
import sys
import threading
def find_peer_once(filename, tracker_ip, tracker_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request = f"GET {filename}.torrent\n"
    udp_socket.sendto(request.encode(), (tracker_ip, tracker_port))
    response, _ = udp_socket.recvfrom(1024)
    metadata = response.decode().split('\n')
    
    peers = set()
    for i in range(2, len(metadata)-1, 2):
        ip = metadata[i].split(': ')[1]
        port = int(metadata[i+1].split(': ')[1])
        peers.add((ip, port))
    udp_socket.close()
    return list(peers)

# def find_peer(filename, tracker_ip, tracker_port):
#     udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     request = f"GET {filename}.torrent\n"
#     udp_socket.sendto(request.encode(), (tracker_ip, tracker_port))
#     while True:
#         mutex.acquire()
#         if len(peers) < 5:
#             response, _ = udp_socket.recvfrom(1024)
#             metadata = response.decode().split('\n')
#             num_blocks = int(metadata[0].split(': ')[1])
#             file_size = int(metadata[1].split(': ')[1])
#             for i in range(2, len(metadata)-1, 2):
#                 ip = metadata[i].split(': ')[1]
#                 port = int(metadata[i+1].split(': ')[1])
#                 peers.add((ip, port))
#         else:
#             break
#         mutex.release()
#     udp_socket.close()
#     return



def get_torrent_metadata(filename, tracker_ip, tracker_port):
    peers = set()
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    

    # Send the torrent metadata request
    request = f"GET {filename}.torrent\n"
    

    counter = 0
    while len(peers) < 5:
        print(f"Discovery round: {counter+1}")
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
        # Sleep for 2 second
        counter += 1
        time.sleep(2)
    udp_socket.close()

    return num_blocks, file_size, list(peers)[:5]

def thread(i, peer, filename):
    global next_seg
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.connect(peer)
    with open(filename, 'wb') as file:
        segment = 0
        body_length = -1
        header_sep = -1

        while next_seg < num_blocks:
            seg.acquire()
            segment = next_seg
            next_seg += 1
            seg.release()
            # Send the block request
            request = f"GET {filename}:{segment}\n"
            peer_socket.send(request.encode())
            
            response = b""
            print(f"Response block: {segment + 1}/{num_blocks}")
            while True:
                try:
                    response += peer_socket.recv(1024)
                    if (body_length == -1 or segment + 1 == num_blocks) and b'\n\n' in response:
                        header_sep = response.index(b'\n\n')
                        header_fields = response[:header_sep].decode().split('\n')
                        if body_length == -1 or segment + 1 == num_blocks:
                            body_length = int(header_fields[2].split(': ')[1])
                    if len(response) > 0 and body_length != -1 and len(response) - header_sep - 2 >= body_length:
                        break
                except socket.timeout:
                    break
                except ConnectionAbortedError:
                    print("Connection closed by host. Rediscovering new peer...")
                    peer_socket.close()
                    new_peer = None
                    mutex.acquire()
                    peer_set.remove(peer)
                    while new_peer is None:
                        discovered = find_peer_once(filename, tracker_ip, tracker_port)
                        if discovered[0] not in peer_set:
                            new_peer = discovered[0]
                            break
                        elif discovered[1] not in peer_set:
                            new_peer = discovered[1]
                            break
                        time.sleep(2)
                    peer_set.add(new_peer)
                    mutex.release()
                    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    peer_socket.connect(new_peer)
                    request = f"GET {filename}:{segment}\n"
                    peer_socket.send(request.encode())
                    response = b""
            # print(response)
            if not response:
                continue
            print(f"successfully retrieved block {segment + 1}")
            # Receive the block response
            header_sep = response.index(b'\n\n')
            header_fields = response[:header_sep].decode().split('\n')
            offset = int(header_fields[1].split(': ')[1])

            # Write the block data to the file at the specified offset
            file.seek(offset)
            file.write(response[header_sep+2:])
            # segment += len(peers)
    peer_socket.close()
    return

def download_file(filename, num_blocks, peers, thread):
    print("Downloading the file...")
    # Create a TCP socket for each peer
    print("Number of peers found: ", len(peers))
    print("Number of blocks: ", num_blocks)
    
    pthreads = [None for _ in range(len(peers))]

    # Create threads and connect to each peer
    for i, peer in enumerate(peers):
        pthreads[i] = threading.Thread(target=thread, args=(i, peer, filename))
        pthreads[i].start()

    # Wait for all threads to finish
    for thread in threading.enumerate():
        if thread != threading.current_thread():
            thread.join()
    

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

    mutex = threading.Semaphore(1)
    seg = threading.Semaphore(1)
    start = time.time()

    num_blocks, file_size, peers = get_torrent_metadata(filename, tracker_ip, tracker_port)
    peer_set = set(peers)
    next_seg = 0
    download_file(filename, num_blocks, peers, thread)
    end = time.time()
    print(f"Downloaded {filename} in {end-start} seconds")