import socket as sk
import time
import struct
import os
import math
import utilities as ut
import random

ut.return_list_of_files_in('file_client')


sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=10000;
server_address = ('localhost', port)
#sock.bind(server_address)
file = 'client.png'
buffer=4096*2
timeoutLimit = 1


sock.settimeout(timeoutLimit)
print("invio")
message = 'invio'
packet=message.encode()
udp_header = struct.pack("!IIII", 1, port, len(packet), ut.checksum_calculator(packet))
sent = sock.sendto(udp_header + packet, server_address)
tot_packs = math.ceil(os.path.getsize(file)/buffer)+1
count=0
var=1
file = open(file, "rb") 


while True:
    
    try:
        print(count)
        chunk= file.read(buffer)
        packet=chunk
        udp_header = struct.pack("!IIII", 2, count, len(packet), ut.checksum_calculator(packet))
        if var % 3:
            sent = sock.sendto(udp_header + packet, server_address)
        else :
            print(count,"perso")
            
        
        rcv, address = sock.recvfrom(buffer)
        received_udp_header = rcv[:16]
        a,b,c,d = struct.unpack('!IIII', received_udp_header)
        while a==4:
            print('qualche errore è successo')
            sent = sock.sendto(udp_header + packet, server_address)
            rcv, address = sock.recvfrom(buffer)
            received_udp_header = rcv[:16]
            a,b,c,d = struct.unpack('!IIII', received_udp_header)

    except sk.timeout:
        print('timeout')
        while True:
            sent = sock.sendto(udp_header + packet, server_address)
            rcv, address = sock.recvfrom(buffer)
            received_udp_header = rcv[:16]
            a,b,c,d = struct.unpack('!IIII', received_udp_header)
            if a==4:
                break
        var+=1
    count+=1
    var+=1
    if count==tot_packs:
        print("inviato ",count," su ",tot_packs)
        break

    
file.close()
   
message = 'inviato'
packet=message.encode()
udp_header = struct.pack("!IIII", 3, tot_packs, len(packet), ut.checksum_calculator(packet))
sent = sock.sendto(udp_header + packet, server_address)
sock.settimeout(None)
print ('closing socket')
sock.close()