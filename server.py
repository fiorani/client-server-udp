import socket as sk
import time
import struct
import os
import math
import zlib
import utilities as ut
from operationType import OperationType as OPType

ut.return_list_of_files_in('file_server')
class server:
    sock=0
    port=0
    buffer=0
    timeoutLimit = 0
    server_address=''
    path = ''
    


    def __init__(self,server_address,port):
       self.port=port
       self.server_address=(server_address,port)
       self.timeoutLimit = 10
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.sock.bind(self.server_address)
       self.path = os.path.join(os.getcwd(), 'file_server')
       
    def get_files(self):
        self.sock.settimeout(self.timeoutLimit)
        print(' list ')
        list_directories = os.listdir(self.path)
        listToStr = ''.join([(str(directory)) for directory in list_directories])
        print(listToStr)
        packet=listToStr.encode()
        udp_header = struct.pack('!IIII', OPType.UPLOAD.value, self.port, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet, self.server_address)      
        print(' -> Sending all the files in the Directory...')
        self.sock.settimeout(None)

    def upload(self,filename,address):
        self.sock.settimeout(self.timeoutLimit)
        self.buffer=4096*2
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/4096)
        count=0
        file = open(os.path.join(self.path, filename), 'rb') 
        while True:
            try:
                chunk= file.read(4096)
                packet=chunk
                udp_header = struct.pack('!IIII', OPType.UPLOAD.value, count, len(packet), ut.checksum_calculator(packet))
                sent = self.sock.sendto(udp_header + packet, address)
                rcv, address = self.sock.recvfrom(self.buffer)
                received_udp_header = rcv[:16]
                a,b,c,d = struct.unpack('!IIII', received_udp_header)
                while a is OPType.NACK.value:
                    print('qualche errore è successo pacchetto',count)
                    sent = self.sock.sendto(udp_header + packet, address)
                    rcv, address = self.sock.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
            except sk.timeout:
                print('timeout pacchetto ',count)
                while True:
                    sent = self.sock.sendto(udp_header + packet, address)
                    rcv, address = self.sock.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
                    if a is OPType.ACK.value:
                        break
            print('inviato pacchetto ',count)
            count+=1
            if count==tot_packs:
                print('inviato ',count,' su ',tot_packs)
                break  
        file.close()
        message = 'inviato'
        packet=message.encode()
        udp_header = struct.pack('!IIII', OPType.CLOSE_CONNECTION.value, tot_packs, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,address)
        self.sock.settimeout(None)
    
    def download(self,filename,address):
        self.sock.settimeout(self.timeoutLimit)
        self.buffer=4096*4
        print('scarico',filename)
        count = 0
        file = open(os.path.join(self.path,filename), 'wb')
        try:
            while True:
                data_rcv, address = self.sock.recvfrom(self.buffer)
                udp_header = data_rcv[:16]
                data = data_rcv[16:]
                a, b, c, d = struct.unpack('!IIII', udp_header)
                correct_checksum = d
                checksum = ut.checksum_calculator(data)
                while correct_checksum != checksum or count != b:
                    print('qualche errore pacchetto ',b)
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
                udp_header = struct.pack('!IIII', OPType.ACK.value, count, 0, 0)
                self.sock.sendto(udp_header,address)
                chunk = data
                file.write(chunk)
                count += 1
                print('ricevuto pacchetto ',b)
            file.close()
            self.sock.settimeout(None)
        except sk.timeout:
            print('timeout')
            self.sock.settimeout(None)
            file.close()
      
        
    def close_server(self):
        print ('closing socket')
        self.sock.close()
        
if __name__ == '__main__':
    server=server('localhost',8080)
    while True:
        print('aspetto')
        data_rcv, address = server.sock.recvfrom(4096*4)
        udp_header = data_rcv[:16]
        data = data_rcv[16:]
        a,b,c,d = struct.unpack('!IIII', udp_header)
        print(a,b)
        if a==OPType.UPLOAD.value:
            server.upload(data.decode('utf8'),address)
        elif a==OPType.DOWNLOAD.value:
            server.download(data.decode('utf8'),address)
        elif a==OPType.CLOSE_CONNECTION.value:  
            server.close_server()
            break;
