import socket as sk
import time
import struct
import os
import zlib


def checksum_calculator(data):
 checksum = zlib.crc32(data)
 return checksum
 

path = os.path.join(os.getcwd(), '') 
if not os.path.exists(os.path.join(path, "file_server")):
   os.mkdir(os.path.join(path, "file_server"))
   path = os.path.join(path, "file_server")



sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
server_address = ('localhost', 10000)
sock.bind(server_address)
print ('\n\r starting up on %s port %s' % server_address)



while True:
    print('\n\r waiting to receive message...')
    
    data_rcv, address = sock.recvfrom(4096)
    udp_header = data_rcv[:16]
    data = data_rcv[16:]
    udp_header = struct.unpack("!IIII", udp_header)
    correct_checksum = udp_header[3]
    checksum = checksum_calculator(data)

    print('received %s bytes from %s' % (len(data), address))
    print (data.decode('utf8'))
    
    if correct_checksum != checksum:
        data1='corrotto'
        time.sleep(2)
        sent = sock.sendto(data1.encode(), address)
        print ('sent %s bytes back to %s' % (sent, address))
    elif data:
        data1='arrivato'
        time.sleep(2)
        sent = sock.sendto(data1.encode(), address)
        print ('sent %s bytes back to %s' % (sent, address))
    else:
        data1='arrivato vuoto'
        time.sleep(2)
        sent = sock.sendto(data1.encode(), address)
        print ('sent %s bytes back to %s' % (sent, address))

