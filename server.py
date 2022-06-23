import socket as sk
import time
import struct
import os
import zlib


def checksum_calculator(data):
 checksum = zlib.crc32(data)
 return checksum
 

if not os.path.exists(os.path.join(os.getcwd(),"file_server")):
   os.mkdir(os.path.join(os.getcwd(), "file_server"))
   

path = os.path.join(os.getcwd(), 'file_server')
file=os.listdir(path)
print(file)

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=10000;
server_address = ('localhost', port)
sock.bind(server_address)
print ('\n\r starting up on %s port %s' % server_address)
buffer=4096


while True:
    print('aspetto')
    data_rcv, address = sock.recvfrom(buffer)
    udp_header = data_rcv[:16]
    data = data_rcv[16:]
    udp_header = struct.unpack("!IIII", udp_header)
    correct_checksum = udp_header[3]
    checksum = checksum_calculator(data)
    print (data.decode('utf8'))
    
    if correct_checksum != checksum:
        print('arrivato corrotto')
    elif data:
        print('connessione stabilità')
        count=0
        data_rcv, address = sock.recvfrom(buffer)
        udp_header = data_rcv[:16]
        data = data_rcv[16:]
        udp_header = struct.unpack("!IIII", udp_header)
        correct_checksum = udp_header[3]
        checksum = checksum_calculator(data)
        if correct_checksum != checksum:
            print("corrotto")
        file= open("server.png", "wb") 
        chunk = data
        while chunk:   
            file.write(chunk)
            count+=1
            data_rcv, address = sock.recvfrom(buffer)
            udp_header = data_rcv[:16]
            data = data_rcv[16:]
            a,b,c,d = struct.unpack("!IIII", udp_header)
            udp_header = struct.unpack("!IIII", udp_header)
            correct_checksum = udp_header[3]
            checksum = checksum_calculator(data)
            if correct_checksum != checksum:
                print("corrotto")
            if a==3:
                print ("arrivati ",count," su ",b)
                break
            chunk = data
            
        file.close
        
    else:
        print('arrivato vuoto')
        
        




