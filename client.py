import socket as sk
import time
import struct
import os
import math
import utilities as ut
import random
from operationType import OperationType as OPType

class Client:

    def __init__(self,server_address,port):
       self.port=port
       self.server_name=server_address
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.sleep=0.001
       self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
       self.directoryName='file_client'
       if not os.path.exists(os.path.join(os.getcwd(), self.directoryName)):
          os.mkdir(os.path.join(os.getcwd(), self.directoryName)) 
       self.path = os.path.join(os.getcwd(), self.directoryName)
    
    def get_self_files(self):
        list_directories = os.listdir(self.path)
        listToStr = ''.join([(str(directory) + '\n') for directory in list_directories])
        print('file ' ,listToStr)
        return listToStr
    
    def get_files_from_server(self):
      self.sock.settimeout(self.timeoutLimit)
      udp_header = struct.pack('!IIII', OPType.GET_SERVER_FILES.value, 0, 0, 0)
      sent = self.sock.sendto(udp_header, self.server_address)
      time.sleep(self.sleep)
      data_rcv, address = self.sock.recvfrom(self.buffer)
      udp_header = data_rcv[:16]
      data = data_rcv[16:]
      udp_header = struct.unpack('!IIII', udp_header)
      correct_checksum = udp_header[3]
      checksum = ut.checksum_calculator(data)
      self.sock.settimeout(None)
      if correct_checksum != checksum:
          return ""
      elif data:
          return data.decode('utf8')
      
    def upload(self,filename):
        if filename in os.listdir(self.path):
            self.sock.settimeout(self.timeoutLimit)
            print('invio nome al server ',filename)
            message = filename
            packet=message.encode()
            tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
            udp_header = struct.pack('!IIII', OPType.DOWNLOAD.value, 0, len(packet), ut.checksum_calculator(packet))
            sent = self.sock.sendto(udp_header + packet,self.server_address)
            time.sleep(self.sleep)
            count=0
            file = open(os.path.join(self.path, filename), 'rb') 
            while True:
                try:
                    chunk= file.read(4096*2)
                    packet=chunk
                    udp_header = struct.pack('!IIII', 0, count, len(packet), ut.checksum_calculator(packet))
                    if random.randint(0, 30)==count:
                        time.sleep(10)
                        print('perso pacchetto',count)
                    else:
                        sent = self.sock.sendto(udp_header + packet, self.server_address)
                        time.sleep(self.sleep)
                    rcv, address = self.sock.recvfrom(self.buffer)
                    received_udp_header = rcv[:16]
                    a,b,c,d = struct.unpack('!IIII', received_udp_header)
                    while a is OPType.NACK.value:
                        print('qualche errore è successo pacchetto',count)
                        sent = self.sock.sendto(udp_header + packet, self.server_address)
                        time.sleep(self.sleep)
                        rcv, address = self.sock.recvfrom(self.buffer)
                        received_udp_header = rcv[:16]
                        a,b,c,d = struct.unpack('!IIII', received_udp_header)
            
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    while True:
                        try:
                            sent = self.sock.sendto(udp_header + packet, self.server_address)
                            time.sleep(self.sleep)
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
            self.sock.settimeout(None)
        else:
            print('non presente  ' ,filename)
        udp_header = struct.pack('!IIII', OPType.CLOSE_CONNECTION.value, tot_packs, 0,0)
        sent = self.sock.sendto(udp_header ,self.server_address)
        time.sleep(self.sleep)
    
    def download(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print('invia nome al server ',filename)
        message = filename
        packet=message.encode()
        udp_header = struct.pack('!IIII', OPType.UPLOAD.value, 0, len(packet), ut.checksum_calculator(packet))
        sent = self.sock.sendto(udp_header + packet,self.server_address)
        time.sleep(self.sleep)
        data_rcv, address = self.sock.recvfrom(self.buffer)
        udp_header = data_rcv[:16]
        data = data_rcv[16:]
        a, b, c, d = struct.unpack('!IIII', udp_header)
        server_address=(self.server_name,b)
        print(server_address)
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
                    self.sock.sendto(udp_header, server_address)
                    time.sleep(self.sleep)
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
                        self.sock.sendto(udp_header, server_address)
                        time.sleep(self.sleep)
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
            self.sock.sendto(udp_header, server_address)
            time.sleep(self.sleep)
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
        time.sleep(self.sleep)
        self.sock.settimeout(None)
        
#if __name__ == '__main__':
#    client=Client('localhost',10000)
#    client.get_files_from_server()
#     client.upload('upload.png')
#     client.download('download.png')
# #     client.close_server()
 #    client.close_client()
    