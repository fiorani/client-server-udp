import socket as sk
import time
import struct
import os
import math
import utilities as ut
from threading import Thread 

ut.return_list_of_files_in('file_client')

sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
port=8080;
server_address = ('localhost', port)
file = 'client.png'
buffer=4096*2

def configura_connessione(msg):
    while True:
        print(msg)
        packet=msg.encode()
        udp_header = struct.pack('!IIII', 1, port, len(packet), ut.checksum_calculator(packet))
        sock.sendto(udp_header + packet, server_address)
        Thread(target=(invia_file), args=('client.png',)).start()

def invia_file(fileName):
    tot_packs = math.ceil(os.path.getsize(fileName)/buffer)+1
    count=0
    file = open(fileName, 'rb') 
    while True:
        chunk = file.read(buffer)
        packet = chunk
        udp_header = struct.pack('!IIII', 2, count, len(packet), ut.checksum_calculator(packet))
        sock.sendto(udp_header + packet, server_address)
        count+=1
        if count==tot_packs:
            print("inviato ",count," su ",tot_packs)
            break
    file.close()
    Thread(target=(termina_invio), args=('Termina invio messaggio...')).start()
  
def termina_invio(msg, tot_packs):
    packet = msg.encode()
    udp_header = struct.pack('!IIII', 3, tot_packs, len(packet), ut.checksum_calculator(packet))
    sock.sendto(udp_header + packet, server_address)
    
try:
    
    Thread(target=(configura_connessione), args=('Inizio invio messaggio...',)).start()

        
except Exception as info:
    print(info)
finally:
    print ('closing socket')
    sock.close()
    
if __name__ == "__main__":
    sock.listen(5)
    print("In attesa di connesioni...")
    sock.close()
    