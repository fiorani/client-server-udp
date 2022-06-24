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
    buffer=0
    timeoutLimit = 0
    server_address=''
    path = ''
    


    def __init__(self,server_address,port):
       self.port=port
       self.server_address=((server_address,port))
       self.timeoutLimit = 10
       self.buffer=4096*4
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.path = os.path.join(os.getcwd(), 'file_client')
       
    def get_files_from_server(self):
      self.sock.settimeout(self.timeoutLimit)
      data_rcv, address = self.sock.recvfrom(self.buffer)
      udp_header = data_rcv[:16]
      data = data_rcv[16:]
      udp_header = struct.unpack('!IIII', udp_header)
      correct_checksum = udp_header[3]
      checksum = ut.checksum_calculator(data)
      if correct_checksum != checksum:
          print('arrivato corrotto')
      elif data:
          print('scarico',data.decode('utf8'))
      self.sock.settimeout(None)

    def upload(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print('invio nome al server ',filename)
        message = filename
        packet=message.encode()
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
        udp_header = struct.pack('!IIII', OPType.DOWNLOAD, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
        count=0
        file = open(os.path.join(self.path, filename), 'rb') 
        while True:
            try:
                chunk= file.read(4096*2)
                packet=chunk
                udp_header = struct.pack('!IIII', OPType.UPLOAD.value, count, len(packet), ut.checksum_calculator(packet))
                if random.randint(0, 100)==count:
                    print('perso pacchetto',count)
                else:
                    sent = self.sock.sendto(udp_header + packet, self.server_address)
                rcv, address = self.sock.recvfrom(self.buffer)
                received_udp_header = rcv[:16]
                a,b,c,d = struct.unpack('!IIII', received_udp_header)
                while a is OPType.NACK.value:
                    print('qualche errore è successo pacchetto',count)
                    sent = self.sock.sendto(udp_header + packet, self.server_address)
                    rcv, address = self.sock.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
        
            except sk.timeout:
                print('timeout pacchetto ',count)
                while True:
                    sent = self.sock.sendto(udp_header + packet, self.server_address)
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
        sent = self.sock.sendto(udp_header + packet,self.server_address)
        self.sock.settimeout(None)
    
    def download(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print('invia nome al server ',filename)
        message = filename
        packet=message.encode()
        udp_header = struct.pack('!IIII', OPType.UPLOAD.value, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
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
                    self.sock.sendto(udp_header, self.server_address)
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
                self.sock.sendto(udp_header, self.server_address)
                chunk = data
                file.write(chunk)
                count += 1
                print('ricevuto pacchetto ',b)
            file.close()
            self.sock.settimeout(None)
        except sk.timeout:
            print('timeout pacchetto ',b)
            self.sock.settimeout(None)
            file.close()
      
        
    def close_client(self):
        message = 'chiusura client'
        self.sock.close()
    def close_server(self):
        self.sock.settimeout(self.timeoutLimit)
        print ('closing socket')
        message = 'chiusura server'
        packet=message.encode()
        udp_header = struct.pack('!IIII', OPType.CLOSE_CONNECTION.value, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
        self.sock.settimeout(None)
        
if __name__ == '__main__':
    client=client('localhost',8080)
    #client.get_files_from_server()
    client.upload('fo.png')
    client.download('mf.png')
    #client.close_server()
    client.close_client()
    