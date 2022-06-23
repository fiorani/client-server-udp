import socket as sk
import time
import struct
import os
import zlib
import math
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
file = 'client.png'
buffer=1024

try:
    
    print("invio")
    message = 'invio'
    packet=message.encode()
    udp_header = struct.pack("!IIII", 1, port, len(packet), checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)
    
    tot_packs = math.ceil(os.path.getsize(file)/buffer)
    count=0
    file = open(file, "rb") 
    chunk= file.read(buffer)
    while chunk:   
        packet=chunk
        udp_header = struct.pack("!IIII", 2, port, len(packet), checksum_calculator(packet))
        sent = sock.sendto(udp_header + packet, server_address)
        chunk = file.read(buffer)
        count+=1
        
    file.close
    
    print("inviato ",count," su ",tot_packs)
    message = 'inviato'
    packet=message.encode()
    udp_header = struct.pack("!IIII", 3, tot_packs, len(packet), checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)

        
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()