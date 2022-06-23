import socket as sk
import time
import struct
import os
import zlib
import utilities as ut

ut.return_list_of_files_in('file_server')
sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=8080;
server_address = ('localhost', port)
sock.bind(server_address)
print ('\n\r starting up on %s port %s' % server_address)
buffer=4096*4


while True:
    print('aspetto')
    data_rcv, address = sock.recvfrom(buffer)
    udp_header = data_rcv[:16]
    data = data_rcv[16:]
    udp_header = struct.unpack("!IIII", udp_header)
    correct_checksum = udp_header[3]
    checksum = ut.checksum_calculator(data)
    print (data.decode('utf8'))
    
    if correct_checksum != checksum:
        print('arrivato corrotto')
    elif data:
        print('connessione stabilità')
        count=0
        file= open("server.png", "wb") 
        while True:             
            data_rcv, address = sock.recvfrom(buffer)
            udp_header = data_rcv[:16]
            data = data_rcv[16:]
            a,b,c,d = struct.unpack("!IIII", udp_header)
            correct_checksum = d
            checksum = ut.checksum_calculator(data)
            if correct_checksum != checksum | b!=count:
                print("corrotto o fuori ordine")
                udp_header = struct.pack('!II', 4, count)
                sock.sendto(udp_header, address)
            elif a==3:
                print ("arrivati ",count," su ",b)
                break
            else:     
                chunk = data
                file.write(chunk)
                count+=1    
        file.close()
        
    else:
        print('arrivato vuoto')
        
        




