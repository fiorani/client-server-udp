import socket as sk
import time
import struct
import os
import math
import zlib
import random
import threading
import utilities as ut
from operationType import OperationType as OPType

ut.return_list_of_files_in('file_server')
class server:

    def __init__(self,server_address,port):
       self.port=port
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.sock.bind(self.server_address)
       
       self.sock2 = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.server_address2=('localhost',8080)
       self.sock2.bind(self.server_address2)
       self.path = os.path.join(os.getcwd(), 'file_server')
       
    def get_files(self, address):
        self.sock.settimeout(self.timeoutLimit)
        print(' list ')
        list_directories = os.listdir(self.path)
        listToStr = ''.join([(str(directory) + '\n') for directory in list_directories])
        print(listToStr)
        packet=listToStr.encode()
        udp_header = struct.pack('!IIII', OPType.GET_SERVER_FILES.value, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet, address)      
        print(' -> Sending all the files in the Directory...')
        self.sock.settimeout(None)

    def upload(self,filename,address):
        self.sock2.settimeout(self.timeoutLimit)
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
        count=0
        file = open(os.path.join(self.path, filename), 'rb') 
        while True:
            try:
                chunk= file.read(4096*2)
                packet=chunk
                udp_header = struct.pack('!IIII', OPType.ACK.value, count, len(packet), ut.checksum_calculator(packet))
                if random.randint(0, 30)==count:
                    time.sleep(10)
                    print('perso pacchetto',count)
                else:
                    sent = self.sock2.sendto(udp_header + packet, address)
                    time.sleep(0.001)
                rcv, address = self.sock2.recvfrom(self.buffer)
                received_udp_header = rcv[:16]
                a,b,c,d = struct.unpack('!IIII', received_udp_header)
                while a is OPType.NACK.value:
                    print('qualche errore è successo pacchetto',count)
                    sent = self.sock2.sendto(udp_header + packet, address)
                    time.sleep(0.001)
                    rcv, address = self.sock2.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
            except sk.timeout:
                print('timeout pacchetto ',count)
                while True:
                    try:
                        sent = self.sock2.sendto(udp_header + packet, address)
                        time.sleep(0.001)
                        rcv, address = self.sock2.recvfrom(self.buffer)
                        received_udp_header = rcv[:16]
                        a,b,c,d = struct.unpack('!IIII', received_udp_header)
                        if a is OPType.ACK.value:
                            break
                    except sk.timeout:
                        print('timeout pacchetto ',count)
            print('inviato pacchetto ',count)
            count+=1
            if count==tot_packs:
                print('inviato ',count,' su ',tot_packs)
                break  
        file.close()
        message = 'inviato'
        packet=message.encode()
        udp_header = struct.pack('!IIII', OPType.CLOSE_CONNECTION.value, tot_packs, len(packet), ut.checksum_calculator(packet))
        sent = self.sock2.sendto(udp_header + packet,address)
        self.sock2.settimeout(None)
    
    def download(self,filename,address):
        self.sock.settimeout(self.timeoutLimit)
        print('scarico',filename)
        count = 0
        file = open(os.path.join(self.path,filename), 'wb')
        while True:
            try:
                data_rcv, address = self.sock.recvfrom(self.buffer)
                udp_header = data_rcv[:16]
                data = data_rcv[16:]
                a, b, c, d = struct.unpack('!IIII', udp_header)
                correct_checksum = d
                checksum = ut.checksum_calculator(data)
                while correct_checksum != checksum or count != b:
                    print('qualche errore pacchetto ',count,'ricevuto pacchetto ',b)
                    udp_header = struct.pack('!IIII', OPType.NACK.value, count, 0, 0)
                    self.sock.sendto(udp_header, address)
                    data_rcv, address = self.sock.recvfrom(self.buffer)
                    udp_header = data_rcv[:16]
                    data = data_rcv[16:]
                    a, b, c, d = struct.unpack('!IIII', udp_header)
                    correct_checksum = d
                    checksum = ut.checksum_calculator(data)
                if a is OPType.CLOSE_CONNECTION.value :
                    print('arrivati ', count, ' su ', b)
                    self.sock.settimeout(None)
                    break
            except sk.timeout:
                print('timeout pacchetto ',count)
                while True:
                    try:
                        udp_header = struct.pack('!IIII', OPType.NACK.value, count, 0, 0)
                        self.sock.sendto(udp_header, address)
                        data_rcv, address = self.sock.recvfrom(self.buffer)
                        udp_header = data_rcv[:16]
                        data = data_rcv[16:]
                        a, b, c, d = struct.unpack('!IIII', udp_header)
                        correct_checksum = d
                        checksum = ut.checksum_calculator(data)
                        if count==b:
                            break
                    except sk.timeout:
                        print('timeout pacchetto ',count) 
            print('ricevuto pacchetto ',count)
            udp_header = struct.pack('!IIII', OPType.ACK.value, count, 0, 0)
            self.sock.sendto(udp_header,address)
            chunk = data
            file.write(chunk)
            count += 1
        file.close()
        self.sock.settimeout(None)
      
        
    def close_server(self):
        print ('closing socket')
        self.sock.close()
        
if __name__ == '__main__':
    server=server('localhost',10000)
    while True:
        server.sock.settimeout(None)
        print('aspetto')
        data_rcv, address = server.sock.recvfrom(server.buffer)
        udp_header = data_rcv[:16]
        data = data_rcv[16:]
        a,b,c,d = struct.unpack('!IIII', udp_header)
        print(a,b)
        if a==OPType.UPLOAD.value:
            #server.upload(data.decode('utf8'),address)
            t = threading.Thread(target=server.upload, args=(data.decode('utf8'),address,))
            t.start()
        elif a==OPType.GET_SERVER_FILES.value:
            server.get_files(address)
        elif a==OPType.DOWNLOAD.value:
            server.download(data.decode('utf8'),address)
            
        elif a==OPType.CLOSE_CONNECTION.value:  
            server.close_server()
            break
