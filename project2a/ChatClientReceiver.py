import socket

# Define the server address and port number
server_address = ('localhost', 12345)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Read the input data from a file or standard input
input_data = b"Hello Batwoman\nHow are you?\nI just heard that Lincoln is set to give a speech in Gettysburg, PA, so we need to rush-deliver the speech transcript to Reuters stations across the country tonight so it makes it in time for the morning papers. Here is the transcript of the Gettysburg address:\nFour score and seven years ago...\nThe end.\nDid you get it okay?"

# Split the input data into segments
segments = [input_data[i:i+2048] for i in range(0, len(input_data), 2048)]

# Send each segment to the server
for segment in segments:
    sock.sendto(segment, server_address)

# Close the socket
sock.close()