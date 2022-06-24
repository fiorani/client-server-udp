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
    server_address=''
    buffer=0
    timeoutLimit = 0
    path = ''
    


    def __init__(self,server_address,port):
       self.port=port
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.server_address=(server_address,port)
       self.sock.bind(self.server_address)
       self.timeoutLimit = 100
       self.buffer=4096
       self.path = os.path.join(os.getcwd(), 'file_server')
       
    def get_files(self):
        self.sock.settimeout(self.timeoutLimit)
        print(' -> Received command : "list files" ')
        list_directories = os.listdir(self.path)
        listToStr = ''.join([(str(directory)) for directory in list_directories])
        print(listToStr)
        packet=listToStr.encode()
        udp_header = struct.pack("!IIII", OPType.UPLOAD.value, self.port, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet, self.server_address)      
        print(' -> Sending all the files in the Directory...')
        self.sock.settimeout(None)

    def upload(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print("invio il file al client ",filename)
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/self.buffer)
        count=0
        file = open(os.path.join(self.path, filename), "rb") 
        while True:
            try:
                print("invio pacchetto ",count)
                chunk= file.read(2048)
                packet=chunk
                udp_header = struct.pack("!IIII", OPType.UPLOAD.value, count, len(packet), ut.checksum_calculator(packet))
                sent = self.sock.sendto(udp_header + packet, self.server_address)                         
                rcv, address = self.sock.recvfrom(self.buffer)
                received_udp_header = rcv[:16]
                a,b,c,d = struct.unpack('!IIII', received_udp_header)
                while a is OPType.NACK.value:
                    print('errore pacchetto ',count)
                    sent = self.sock.sendto(udp_header + packet, self.server_address)
                    rcv, address = self.sock.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
        
            except sk.timeout:
                print('timeout pacchetto ', count)
                while True:
                    sent = self.sock.sendto(udp_header + packet, self.server_address)
                    rcv, address = self.sock.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
                    if a is OPType.ACK.value:
                        break
            count+=1
            if count==tot_packs:
                print("inviati ",count," su ",tot_packs)
                break
            
        file.close()
        message = 'inviato tutto'
        packet=message.encode()
        udp_header = struct.pack("!IIII", OPType.CLOSE_CONNECTION.value, tot_packs, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet, self.server_address)
        self.sock.settimeout(None)
    
    def download(self,filename):
        self.buffer=4096*2
        self.sock.settimeout(self.timeoutLimit)
        print('scarico',filename)
        count = 0
        file = open(os.path.join(self.path,filename), "wb")
        
        while True:
            try:
                data_rcv, address = self.sock.recvfrom(self.buffer)
                udp_header = data_rcv[:16]
                data = data_rcv[16:]
                a, b, c, d = struct.unpack("!IIII", udp_header)
                correct_checksum = d
                checksum = ut.checksum_calculator(data)
                while correct_checksum != checksum or count != b:
                    print('errore pacchetto ',count)
                    udp_header = struct.pack('!IIII', OPType.NACK.value, count, 0, 0)
                    self.sock.sendto(udp_header, address)
                    data_rcv, address = self.sock.recvfrom(self.buffer)
                    udp_header = data_rcv[:16]
                    data = data_rcv[16:]
                    a, b, c, d = struct.unpack("!IIII", udp_header)
                    correct_checksum = d
                    checksum = ut.checksum_calculator(data)
                if a is OPType.CLOSE_CONNECTION.value :
                    print("arrivati ", count, " su ", b)
                    self.sock.settimeout(None)
                    break
            except sk.timeout:
                print("timeout pacchetto ", count)
                while correct_checksum != checksum or count != b:
                    udp_header = struct.pack('!IIII', OPType.NACK.value, count, 0, 0)
                    self.sock.sendto(udp_header, address)
                    data_rcv, address = self.sock.recvfrom(self.buffer)
                    udp_header = data_rcv[:16]
                    data = data_rcv[16:]
                    a, b, c, d = struct.unpack("!IIII", udp_header)
                    correct_checksum = d
                    checksum = ut.checksum_calculator(data)
                
            udp_header = struct.pack('!IIII', OPType.ACK.value, count, 0, 0)
            self.sock.sendto(udp_header, address)
            chunk = data
            file.write(chunk)
            count += 1
            print("arrivato pacchetto " , b)
        file.close()
        
        self.sock.settimeout(None)
      
        
    def close_server(self):
        self.sock.settimeout(None)
        print ('closing socket')
        self.sock.close()
        
if __name__ == "__main__":
    server=server('localhost',10000)
    while True:
        try:
            print("aspetto")
            data_rcv, address = server.sock.recvfrom(4096*4)
            udp_header = data_rcv[:16]
            data = data_rcv[16:]
            a,b,c,d = struct.unpack("!IIII", udp_header)
            print(a,b)
            if a==OPType.UPLOAD.value:
                server.upload(data.decode('utf8'))
            elif a==OPType.DOWNLOAD.value:
                server.download(data.decode('utf8'))
            elif a==OPType.CLOSE_CONNECTION.value:  
                server.close_server()
            

        except sk.timeout:
            print("timeout")
