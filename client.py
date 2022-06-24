import socket as sk
import time
import struct
import os
import math
import utilities as ut
import random
from operationType import OperationType as OPType

ut.return_list_of_files_in('file_client')
class client:
    sock=0
    port=0
    server_address=''
    buffer=0
    timeoutLimit = 0
    path = ''
    


    def __init__(self,server_address,port):
       self.port=port
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.server_address=((server_address,port))
       #self.sock.bind(self.server_address)
       self.timeoutLimit = 100
       self.buffer=4096
       self.path = os.path.join(os.getcwd(), 'file_client')
       
    def get_files_from_server(self):
      self.sock.settimeout(self.timeoutLimit)
      data_rcv, address = self.sock.recvfrom(self.buffer)
      udp_header = data_rcv[:16]
      data = data_rcv[16:]
      udp_header = struct.unpack("!IIII", udp_header)
      correct_checksum = udp_header[3]
      checksum = ut.checksum_calculator(data)
      if correct_checksum != checksum:
          print('arrivato corrotto')
      elif data:
          print('scarico',data.decode('utf8'))
      self.sock.settimeout(None)

    def upload(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print("invio ",filename)
        message = filename
        packet=message.encode()
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/self.buffer)
        udp_header = struct.pack("!IIII", OPType.DOWNLOAD, tot_packs, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
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
        udp_header = struct.pack("!IIII", OPType.UPLOAD.value, tot_packs, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet, self.server_address)
        self.sock.settimeout(None)
    
    def download(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print("invia nome al server ",filename)
        message = filename
        packet=message.encode()
        udp_header = struct.pack("!IIII", OPType.UPLOAD.value, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
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
                
            chunk = data
            file.write(chunk)
            count += 1
            print("arrivato pacchetto " , b)
        file.close()
        self.sock.settimeout(None)
      
        
    def close_client(self):
        self.sock.settimeout(None)
        print ('closing socket')
        self.sock.close()
        
if __name__ == "__main__":
    client=client('localhost',10000)
    
    #client.get_files_from_server()
    #client.upload("client.png")
    client.download("client.png")
    client.close_client()