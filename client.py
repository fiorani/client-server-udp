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
    print(msg)
    packet=msg.encode()
    udp_header = struct.pack('!IIII', 1, port, len(packet), ut.checksum_calculator(packet))
    sock.sendto(udp_header + packet, server_address)
    ACCEPT_THREAD=Thread(target=invia_file, args=('client.png',))
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()

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
    ACCEPT_THREAD=Thread(target=termina_invio, args=('Termina invio messaggio...',tot_packs,))
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
  
def termina_invio(msg, tot_packs):
    packet = msg.encode()
    udp_header = struct.pack('!IIII', 3, tot_packs, len(packet), ut.checksum_calculator(packet))
    sock.sendto(udp_header + packet, server_address)
    
if __name__ == "__main__":
    ACCEPT_THREAD = Thread(target=configura_connessione, args=('Inizio invio messaggio...',))
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    print("In attesa di connesioni...")
    sock.close()
    