import socket as sk
from socket import error as sock_err
import time
import struct
import os
import math
import random
import threading
import utilities as ut
from serverMenu import Ui
from operationType import OperationType as OPType
from segmentFactory import SegmentFactory
class Server:

    def __init__(self,server_address,port):
       self.portsList = [50_000, 50_001, 50_002, 50_003, 50_004, 50_005, 50_006, 50_007, 50_008, 50_009]
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.sleep=0.001
       self.lock = threading.Lock()
       self.directoryName='file_server'
       ut.create_directory(self.directoryName)
       self.path = os.path.join(os.getcwd(), self.directoryName)
    
    def send(self,sock,address, segment):
       self.sock.sendto(segment, address)  
       time.sleep(self.sleep)
       
    def rcv(self,sock):
        rcv, address = sock.recvfrom(self.buffer)
        received_udp_header = rcv[:16]
        data = rcv[16:]
        op,port,count,checksum_correct = struct.unpack('!IIII', received_udp_header)
        checksum = ut.checksum_calculator(data)
        return data,address,checksum,op,count,port,checksum_correct
   
    def occupy_port(self):
        self.lock.acquire()
        if len(self.portsList) > 0:
            #Senza argomenti, pop() rimuove l'ultimo elemento della lista
            port = self.portsList.pop()
        else:
            #nel thread su cui serve occupare la porta controlla sempre che la porta sia != -1
            port = -1
        self.lock.release()
        return port
    
    def release_port(self, port):
        self.lock.acquire()
        self.portsList.append(port)
        self.lock.release()  
     
    def get_self_files(self):
        listToStr = ''.join([(str(directory) + '\n') for directory in os.listdir(self.path)])
        print('file ' ,listToStr)
        return listToStr
        
    def get_files(self, address):
        self.sock.settimeout(self.timeoutLimit)
        print('invio al client  ' ,self.get_self_files())
        self.send(self.sock,address,SegmentFactory.getListOfFilesSegment(self.get_self_files()))
        self.sock.settimeout(None)
        
    def upload(self,filename,address):
        port=self.occupy_port()
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,address, SegmentFactory.getBeginConnectionSegment(port, tot_packs))
        self.sock.settimeout(None)
        server_address=(self.server_address[0],port)
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.bind(server_address)
        sock.settimeout(self.timeoutLimit)        
        print('invio al client  ' ,filename)
        count=0
        tries=0
        with open(os.path.join(self.path, filename), 'rb') as file:
            chunk= file.read(4096*2)
            while True:
                try:
                    #if random.randint(0, 30)==count:
                    #    time.sleep(10)
                    #    print('perso pacchetto',count)
                    #else:
                    self.send(sock,address,SegmentFactory.getUploadChunkSegment(count, chunk))
                    data,address,checksum,op,c,p,checksum_correct = self.rcv(sock)
                    if op==OPType.NACK.value:
                        print('qualche errore è successo pacchetto',count)
                    else:
                        chunk= file.read(4096*2)
                        print('inviato pacchetto ',count)
                        count+=1
                        tries=0
                        if count==tot_packs:
                            print('inviati ',count,' su ',tot_packs)
                            break  
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    tries+=1
                    if(tries==5):
                        print('upload fallito ')
                        break
                    
        self.send(sock,address,SegmentFactory.getCloseConnectionSegment())
        sock.settimeout(None)
        sock.close()
        self.release_port(port)
    
    def download(self,filename,address):
        port=self.occupy_port()
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,address,SegmentFactory.getBeginConnectionSegment(port, 0))
        self.sock.settimeout(None)
        server_address=(self.server_address[0],port)
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.bind(server_address)
        sock.settimeout(self.timeoutLimit)
        print('scarico dal client',filename)
        count = 0
        tries=0
        with open(os.path.join(self.path, filename), 'wb') as file:
            while True:
                try:
                    data,address,checksum,op,c,p,checksum_correct = self.rcv(sock)
                    if checksum_correct != checksum or count != c:
                        print('qualche errore pacchetto ',count,'ricevuto pacchetto ',c)
                        self.send(sock,address, SegmentFactory.getNACKSegment(count))
                    else:
                        if op is OPType.CLOSE_CONNECTION.value :
                            print('arrivati ', count, ' su ', c)
                            sock.settimeout(None)
                            break
                        print('ricevuto pacchetto ',count)
                        self.send(sock,address,SegmentFactory.getACKSegment(count))
                        file.write(data)
                        count += 1 
                        tries=0
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    tries+=1
                    if(tries==5):
                        print('download fallito ')
                        file.close()
                        os.remove(os.path.join(self.path, filename))
                        break
                    
                 
        sock.settimeout(None)
        sock.close()
        self.release_port(port)
      
    def start_server(self):
        print ('start socket')
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        threading.Thread(target=self.server_main_loop).start()
    
    def close_server(self):
        print ('closing socket')
        self.sock.settimeout(None)
        self.sock.close()
    
    def server_main_loop(self):
        try:
            while True:    
                self.sock.settimeout(None)
                print('aspetto')
                data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
                if op==OPType.UPLOAD.value:
                    #server.upload(data.decode('utf8'),address)
                    threading.Thread(target=self.upload, args=(data.decode('utf8'),address,)).start()
                elif op==OPType.GET_SERVER_FILES.value:
                    print(address)
                    self.get_files(address)
                elif op==OPType.DOWNLOAD.value:
                    threading.Thread(target=self.download, args=(data.decode('utf8'),address,)).start()
                    #self.download(data.decode('utf8'),address)
        except sock_err:
            #necessario per non avere eccezioni qualora si chiudesse il socket
            print('closing server')
                
            
    
if __name__ == '__main__':
     server=Server('localhost',10000)
     threading.Thread(target=Ui,args=(server,)).start()
         