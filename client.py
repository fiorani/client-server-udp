import socket as sk
import time
import struct
import os
import zlib
def checksum_calculator(data):
 checksum = zlib.crc32(data)
 return checksum


if not os.path.exists(os.path.join(os.getcwd(), "file_client")):
   os.mkdir(os.path.join(os.getcwd(), "file_client"))
   
path = os.path.join(os.getcwd(), 'file_client')
print(os.listdir(path))

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=10000;
server_address = ('localhost', port)
message = 'client.png'
buffer=2048

try:
    packet=message.encode()
    udp_header = struct.pack("!IIII", port, port, len(packet), checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)
    file = open(message, "rb") 
    chunk= file.read(buffer)
    while chunk:   
        packet=chunk
        udp_header = struct.pack("!IIII", port, port, len(packet), checksum_calculator(packet))
        sent = sock.sendto(udp_header + packet, server_address)
        chunk = file.read(buffer)
        
    file.close

        
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()