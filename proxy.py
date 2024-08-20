import sys  # Importing the sys module for system-specific parameters and functions
import socket  # Importing the socket module for network communication
import threading  # Importing the threading module to handle multiple connections

# Create a filter for printable characters in hexadecimal representation
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

# Function to create a hexdump of the given source data
def hexdump(src, length=16, sep='.'):
    # If the source is in bytes, decode it to a string
    if isinstance(src, bytes):
        src = src.decode()
        
    results = list()  # List to store the hexdump lines
    for i in range(0, len(src), length):
        word = str(src[i:i+length])  # Extract a segment of the source data

        # Translate the segment to printable characters
        printable = word.translate(HEX_FILTER)
        # Convert the segment to hexadecimal representation
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3  # Calculate the width for the hex part
        # Append the formatted line to the results list
        results.append(f'{i:04X} {hexa:<{hexwidth}} {printable}')
    
    if show:
        # Print each line of the hexdump
        for line in results:
            print(line)
    else:
        # Return the list of hexdump lines
        return results

def receive_from(connection):
    buffer = b""  # Buffer to store the received data
    connection.settimeout(5)  # Set a timeout for the connection
    try:
        while True:
            data = connection.recv(4096)  # Receive data from the connection
            if not data:
                break  # Exit the loop if no data is received
            buffer += data  # Append the received data to the buffer
    except Exception as e:
        pass  # Ignore any exceptions
    return buffer  # Return the received data

def request_handler(buffer):
    # Perform packet modifications
    return buffer  # Return the buffer as is

def response_handler(buffer):
    # Perform packet modifications
    return buffer  # Return the buffer as is

def proxy_handler(client_socket, remote_host, remote_port, receive_first):  # Function to handle the proxy connection
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
    remote_socket.connect((remote_host, remote_port))  # Connect to the remote host

    if receive_first:
        remote_buffer = receive_from(remote_socket)  # Receive data from the remote host
        hexdump(remote_buffer)  # Print the hexdump of the received data

    remote_buffer = response_handler(remote_buffer)  # Handle the received data
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))  # Log the data being sent to the local client
        client_socket.send(remote_buffer)  # Send the data to the local client

    while True:
        local_buffer = receive_from(client_socket)  # Receive data from the local client
        if len(local_buffer):
            line = "[==>] Received %d bytes from local." % len(local_buffer)  # Log the data received from the local client
            print(line)
            hexdump(local_buffer)  # Print the hexdump of the received data

            local_buffer = request_handler(local_buffer)  # Handle the received data
            remote_socket.send(local_buffer)  # Send the data to the remote server
            print("[==>] sent to remote.")  # Log the data being sent to the remote server

        remote_buffer = receive_from(remote_socket)  # Receive data from the remote server
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))  # Log the data received from the remote server
            hexdump(remote_buffer)  # Print the hexdump of the received data

            remote_buffer = response_handler(remote_buffer)  # Handle the received data
            client_socket.send(remote_buffer)  # Send the data to the local client
            print("[<==] sent to local.")  # Log the data being sent to the local client

def request_handler(buffer):
    # Perform packet modifications
    return buffer  # Return the buffer as is

def response_handler(buffer):
    # Perform packet modifications
    return buffer  # Return the buffer as is

def proxy_handler(client_socket, remote_host, remote_port, receive_first):  # Function to handle the proxy connection
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
    remote_socket.connect((remote_host, remote_port))   # Connect to the remote host

    if receive_first:
        remote_buffer = receive_from(remote_socket)  # Receive data from the remote host
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)  # Handle the received data
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from local." %len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] sent to local.")

        if not len(local_buffer)or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break
        
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d:" (local_host, local_port))
    server.listen(5)  # Listen for incoming connections
    while True:
        client_socket, addr = server.accept()
        #print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        #start a thread to talk to the remote host
        proxy_thread = threading.Thread(target = proxy_handler, args = (client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) !=5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 1270.0.01 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port,receive_first)

if __name__ == '__main__':
    main()

    
    