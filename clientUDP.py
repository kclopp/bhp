import socket

rhost = "172.0.0.1"

rport = 9997

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b"AAABBBCCC",(rhost, rport))

data, addr = client.recvfrom(4096)

print(data.decode())
client.close()

