import socket as sk
import time
import struct
import os
import zlib
def checksum_calculator(data):
 checksum = zlib.crc32(data)
 return checksum


if not os.path.exists(os.path.join('', "file_client")):
   os.mkdir(os.path.join('', "file_client"))
   

path = os.path.join(os.getcwd(), 'file_client')
file=os.listdir(path)
print(file)

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=10000;
server_address = ('localhost', port)
message = 'bella'

try:

    # inviate il messaggio
    print ('sending "%s"' % message)
    time.sleep(2) #attende 2 secondi prima di inviare la richiesta
    packet=message.encode()
    checksum = checksum_calculator(packet)
    data_length = len(packet)
    udp_header = struct.pack("!IIII", port, port, data_length, checksum)
    #test corrotto
    message = 'bel'
    packet=message.encode()
    packet_with_header = udp_header + packet
    sent = sock.sendto(packet_with_header, server_address)

    # Ricevete la risposta dal server
    print('waiting to receive from')
    data, server = sock.recvfrom(4096)
    #print(server)
    time.sleep(2)
    print ('received message "%s"' % data.decode('utf8'))
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()