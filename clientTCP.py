import socket

rhost = "192.168.70.129"

rport=5555

client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((rhost,rport))

client.send(b"GET / HTTP/1.1/r/nHost: google.com/r/n/r/n")

response=client.recv(4096)

print(response.decode())

client.close()
