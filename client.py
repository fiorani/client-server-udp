import socket as sk
import time
import struct
import os
import math
import utilities as ut

ut.return_list_of_files_in('file_client')

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=10000;
server_address = ('localhost', port)
file = 'client.png'
buffer=4096*2

try:
    
    print("invio")
    message = 'invio'
    packet=message.encode()
    udp_header = struct.pack("!IIII", 1, port, len(packet), ut.checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)
    
    tot_packs = math.ceil(os.path.getsize(file)/buffer)+1
    count=0
    file = open(file, "rb") 
    
    while True:
        chunk= file.read(buffer)
        packet=chunk
        udp_header = struct.pack("!IIII", 2, count, len(packet), ut.checksum_calculator(packet))
        sent = sock.sendto(udp_header + packet, server_address)
        count+=1
        if count==tot_packs:
            print("inviato ",count," su ",tot_packs)
            break
        
    file.close()
   
    message = 'inviato'
    packet=message.encode()
    udp_header = struct.pack("!IIII", 3, tot_packs, len(packet), ut.checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)

        
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()