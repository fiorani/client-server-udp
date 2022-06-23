import socket as sk
import time
import struct
import os
import math
import utilities as ut

ut.return_list_of_files_in('file_client')


sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=10000;
server_address = ('riccardofiorani.ddns.net', port)
#sock.bind(server_address)
file = 'download.mp4'
buffer=4096*2

try:
    
    print("invio")
    message = 'invio'
    packet=message.encode()
    udp_header = struct.pack("!IIII", 1, port, len(packet), ut.checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)
    sock.settimeout(10)
    tot_packs = math.ceil(os.path.getsize(file)/buffer)+1
    count=0
    file = open(file, "rb") 
    
    while True:
        chunk= file.read(buffer)
        packet=chunk
        udp_header = struct.pack("!IIII", 2, count, len(packet), ut.checksum_calculator(packet))
        sent = sock.sendto(udp_header + packet, server_address)
        sock.settimeout(10)        
        rcv, address = sock.recvfrom(buffer)
        received_udp_header = rcv[:16]
        a,b,c,d = struct.unpack('!IIII', received_udp_header)
        while a==4:
            sent = sock.sendto(udp_header + packet, server_address)
            sock.settimeout(10)
            rcv, address = sock.recvfrom(buffer)
            received_udp_header = rcv[:16]
            a,b,c,d = struct.unpack('!IIII', received_udp_header)
          
        count+=1
        if count==tot_packs:
            print("inviato ",count," su ",tot_packs)
            break
        
    file.close()
   
    message = 'inviato'
    packet=message.encode()
    udp_header = struct.pack("!IIII", 3, tot_packs, len(packet), ut.checksum_calculator(packet))
    sent = sock.sendto(udp_header + packet, server_address)
    sock.settimeout(10)
        
except sk.timeout:
    print ('timeout')
    sock.close()
finally:
    print ('closing socket')
    sock.close()