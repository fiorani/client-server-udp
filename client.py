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
from segmentFactory import SegmentFactory

class Client:

    def __init__(self,server_address,port):
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.perc=0
       self.sleep=0.01
       self.directoryName='file_client'
       ut.create_directory(self.directoryName)
       self.path = os.path.join(os.getcwd(), self.directoryName)
    
    def send(self,sock,address,segment):
       self.sock.sendto(segment, address)  
       time.sleep(self.sleep)
       
    def rcv(self,sock):
        rcv, address = sock.recvfrom(self.buffer)
        received_udp_header = rcv[:16]
        data = rcv[16:]
        op,port,count,checksum_correct = struct.unpack('!IIII', received_udp_header)
        checksum = ut.checksum_calculator(data)
        return data,address,checksum,op,count,port,checksum_correct
    
    def get_self_files(self):
        listToStr = ''.join([(str(directory) + '\n') for directory in os.listdir(self.path)])
        print('file ' ,listToStr)
        return listToStr
    
    def get_files_from_server(self):
      self.sock.settimeout(self.timeoutLimit)
      self.send(self.sock,self.server_address,SegmentFactory.getFileRequestSegment())
      data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
      self.sock.settimeout(None)
      if checksum_correct != checksum:
          return ""
      elif data:
          return data.decode('utf8')
      
    def upload(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print('invio nome al server ',filename)
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
        self.send(self.sock,self.server_address, SegmentFactory.getBeginUploadToServerSegment(filename, tot_packs))
        data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
        port=p
        server_address=(self.server_address[0],port)
        print('indirizzo ',server_address)
        count=0
        tries=0
        with open(os.path.join(self.path, filename), 'rb') as file:
            chunk= file.read(4096*2)
            self.send(self.sock,server_address,SegmentFactory.getUploadChunkSegment(count, chunk))
            print('inviato pacchetto ',count)
            self.perc=int(count*100/tot_packs)
            count+=1
            while True:
                try:
                    #if random.randint(0, 30)==count:
                    #    time.sleep(10)
                    #    print('perso pacchetto',count)
                    #else:
                    data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
                    if op==OPType.NACK.value:
                        print('qualche errore è successo pacchetto',count)
                        self.send(self.sock,server_address,SegmentFactory.getUploadChunkSegment(count, chunk))
                    elif count==tot_packs:
                        self.perc=100
                        print('inviato ',count,' su ',tot_packs)
                        break
                    elif op==OPType.ACK.value:
                        chunk= file.read(4096*2)
                        self.send(self.sock,server_address,SegmentFactory.getUploadChunkSegment(count, chunk))
                        print('inviato pacchetto ',count)
                        self.perc=int(count*100/tot_packs)
                        count+=1
                        tries=0
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    tries+=1
                    if(tries==5):
                        print('upload fallito ')
                        break
                    
            
        self.send(self.sock,server_address,SegmentFactory.getCloseConnectionSegment())
        self.sock.settimeout(None)
    
    def download(self,filename):
        self.sock.settimeout(self.timeoutLimit)
        print('invia nome al server ',filename)
        self.send(self.sock,self.server_address, SegmentFactory.getUploadRequestSegment(filename))
        data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
        tot_packs=c
        port=p
        server_address=(self.server_address[0],port)
        print('indirizzo ',server_address)
        count = 0
        tries=0
        with open(os.path.join(self.path, filename), 'wb') as file:
            while True:
                try:
                    data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
                    if op is OPType.CLOSE_CONNECTION.value :
                        print('arrivati ', count, ' su ', tot_packs)
                        self.sock.settimeout(None)
                        break
                    elif checksum_correct != checksum or count != c:
                        print('qualche errore pacchetto ',count,'ricevuto pacchetto ',count)
                        self.send(self.sock,server_address,SegmentFactory.getNACKSegment(count))
                    else:
                        print('ricevuto pacchetto ',count)
                        self.send(self.sock,server_address,SegmentFactory.getACKSegment(count))
                        file.write(data)
                        count += 1
                        self.perc=int(count*100/tot_packs)
                        tries=0
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    self.send(self.sock,server_address,SegmentFactory.getNACKSegment(count))
                    tries+=1
                    if(tries==5):
                        print('download fallito ')
                        file.close()
                        os.remove(os.path.join(self.path, filename))
                        break
                    
                
        self.sock.settimeout(None)
    
    def status(self):
        return self.perc
      
    def start_client(self):
        print('avvio client')
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        
    def close_client(self):
        print('chiusura client')
        self.sock.settimeout(None)
        self.sock.close()
        
        
if __name__ == '__main__':
    client=Client('localhost',10000)
    threading.Thread(target=Ui,args=(client,)).start()
    