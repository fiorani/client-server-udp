import socket as sk
import time
import struct
import os
import math
import utilities as ut
import random
import threading
from clientMenu import Ui
from operationType import OperationType as OPType

class Client:

    def __init__(self,server_address,port):
       self.client_address=(server_address,0)
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.sleep=0.001
       self.directoryName='file_client'
       if not os.path.exists(os.path.join(os.getcwd(), self.directoryName)):
          os.mkdir(os.path.join(os.getcwd(), self.directoryName)) 
       self.path = os.path.join(os.getcwd(), self.directoryName)
    
    def send(self,sock,address,data,op,count):
       header = struct.pack('!IIII', op, count, len(data), ut.checksum_calculator(data))
       self.sock.sendto(header + data, address)  
       time.sleep(self.sleep)
       
    def rcv(self,sock):
        rcv, address = sock.recvfrom(self.buffer)
        received_udp_header = rcv[:16]
        data = rcv[16:]
        a,b,c,d = struct.unpack('!IIII', received_udp_header)
        checksum = ut.checksum_calculator(data)
        return data,address,checksum,a,b,c,d
    
    def get_self_files(self):
        listToStr = ''.join([(str(directory) + '\n') for directory in os.listdir(self.path)])
        print('file nel client' ,listToStr)
        return listToStr
    
    def get_files_from_server(self):
      self.sock.settimeout(self.timeoutLimit)
      self.send(self.sock,self.server_address,'chiedo file'.encode(),OPType.GET_SERVER_FILES.value,0)
      data,address,checksum,a,b,c,d = self.rcv(self.sock)
      self.sock.settimeout(None)
      if d != checksum:
          return ""
      elif data:
          print('file nel server' ,data.decode('utf8'))
          return data.decode('utf8')
      
    def upload(self,filename):
        if filename in os.listdir(self.path):
            self.sock.settimeout(self.timeoutLimit)
            print ('upload client porta',self.client_address[1])
            print('invio nome al server ',filename)
            tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
            self.send(self.sock,self.server_address,filename.encode(),OPType.DOWNLOAD.value,self.client_address[1])
            count=0
            with open(os.path.join(self.path, filename), 'rb') as file:
                while True:
                    try:
                        chunk= file.read(4096*2)
                        #if random.randint(0, 30)==count:
                        #    time.sleep(10)
                        #    print('perso pacchetto',count)
                        #else:
                        #    self.send(self.sock,self.client_address,chunk,0,count)
                        self.send(self.sock,self.client_address,chunk,0,count)
                        data,address,checksum,a,b,c,d = self.rcv(self.sock)
                        while a is OPType.NACK.value:
                            print('qualche errore è successo pacchetto',count)
                            self.send(self.sock,self.client_address,chunk,0,count)
                            data,address,checksum,a,b,c,d = self.rcv(self.sock)
                
                    except sk.timeout:
                        print('timeout pacchetto ',count)
                        while True:
                            try:
                                self.send(self.sock,self.client_address,chunk,0,count)
                                data,address,checksum,a,b,c,d = self.rcv(self.sock)
                                if a is OPType.ACK.value:
                                    break
                            except sk.timeout:
                                print('timeout pacchetto ',count)
                    print('inviato pacchetto ',count)
                    count+=1
                    if count==tot_packs:
                        print('inviato ',count,' su ',tot_packs)
                        break
        else:
            print('non presente  ' ,filename)
        self.send(self.sock,self.client_address,'chiudo la connessione'.encode(),OPType.CLOSE_CONNECTION.value,tot_packs)
        self.sock.settimeout(None)
    
    def download(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print ('upload client porta',self.client_address[1])
        print('invia nome al server ',filename)
        self.send(self.sock,self.server_address,filename.encode(),OPType.UPLOAD.value,self.client_address[1])
        self.send(self.sock,self.client_address,'invio il nuovo address'.encode(),0,0)
        count = 0
        with open(os.path.join(self.path, filename), 'wb') as file:
            while True:
                try:
                    data,address,checksum,a,b,c,d = self.rcv(self.sock)
                    while d != checksum or count != b:
                        print('qualche errore pacchetto ',count,'ricevuto pacchetto ',b)
                        self.send(self.sock,self.client_address,'NACK'.encode(),OPType.NACK.value,count)
                        data,address,checksum,a,b,c,d = self.rcv(self.sock)
                    if a is OPType.CLOSE_CONNECTION.value :
                        print('arrivati ', count, ' su ', b)
                        self.sock.settimeout(None)
                        break
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    while True:
                        try:
                            self.send(self.sock,self.client_address,'NACK'.encode(),OPType.NACK.value,count)
                            data,address,checksum,a,b,c,d = self.rcv(self.sock)
                            if count==b:
                                break
                        except sk.timeout:
                            print('timeout pacchetto ',count)
                print('ricevuto pacchetto ',count)
                self.send(self.sock,self.client_address,'ACK'.encode(),OPType.ACK.value,count)
                file.write(data)
                count += 1
        self.sock.settimeout(None)
      
    def start_client(self):
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,self.server_address,'inizio connessione'.encode(),OPType.BEGIN_CONNECTION.value,0)
        data,address,checksum,a,b,c,d = self.rcv(self.sock)
        print('avvio client porta ',b)
        self.client_address=(self.server_address[0],b)
        self.sock.settimeout(None)
        
    def close_client(self):
        print('chiusura client')
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,self.server_address,'chiudo connessione'.encode(),OPType.CLOSE_CONNECTION.value,self.client_address[1])
        self.sock.settimeout(None)
        self.sock.close()
        
        
if __name__ == '__main__':
    client=Client('10.0.0.20',10000)
    threading.Thread(target=Ui,args=(client,)).start()
    