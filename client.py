import socket as sk
import time
import struct
import os
import math
import utilities as ut
import random
import threading
from operationType import OperationType as OPType

ut.return_list_of_files_in('file_client')
class client:

    def __init__(self,server_address,port):
       self.port=port
       self.server_address=((server_address,port))
       self.timeoutLimit = 3
       self.buffer=4096*4
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.path = os.path.join(os.getcwd(), 'file_client')
       
    def get_files_from_server(self):
      self.sock.settimeout(self.timeoutLimit)
      udp_header = struct.pack('!IIII', OPType.GET_SERVER_FILES.value, 0, 0, 0)
      print('richiedo lista dei files...')
      sent = self.sock.sendto(udp_header, self.server_address)
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
        udp_header = struct.pack('!IIII', OPType.DOWNLOAD.value, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
        count=0
        file = open(os.path.join(self.path, filename), 'rb') 
        while True:
            try:
                chunk= file.read(4096*2)
                packet=chunk
                udp_header = struct.pack('!IIII', OPType.UPLOAD.value, count, len(packet), ut.checksum_calculator(packet))
                if random.randint(0, 30)==count:
                    time.sleep(10)
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
                    try:
                        sent = self.sock.sendto(udp_header + packet, self.server_address)
                        rcv, address = self.sock.recvfrom(self.buffer)
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
            except sk.timeout:
                print('timeout pacchetto ',count)
                while True:
                    try:
                        udp_header = struct.pack('!IIII', OPType.NACK.value, count, 0, 0)
                        self.sock.sendto(udp_header, self.server_address)
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
            self.sock.sendto(udp_header, self.server_address)
            chunk = data
            file.write(chunk)
            count += 1
                
        file.close()
        self.sock.settimeout(None)
        
      
        
    def close_client(self):
        message = 'chiusura client'
        print(message)
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
    client=client('localhost',10000)
    client.get_files_from_server()
    #client.upload('client.png')
    client.download('client.png')
    #client.close_server()
    client.close_client()
    