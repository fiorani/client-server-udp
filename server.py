import socket as sk
import time
import struct
import os
import math
import random
import threading
import utilities as ut
from serverMenu import Ui
from operationType import OperationType as OPType

class Server:

    def __init__(self,server_address,port):
       self.portsList = [50_000, 50_001, 50_002, 50_003, 50_004, 50_005, 50_006, 50_007, 50_008, 50_009]
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.sleep=0.001
       self.lock = threading.Lock()
       self.directoryName='file_server'
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
        listToStr = ''.join([(str(directory) + '\n') for directory in os.listdir(self.path)])
        print('invio al client  ' ,listToStr)
        self.send(self.sock,address,listToStr.encode(),OPType.GET_SERVER_FILES.value,0)
        self.sock.settimeout(None)
        
    def upload(self,filename,address):
        port=self.occupy_port()
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,address,'invio porta'.encode(),0,port)
        self.sock.settimeout(None)
        server_address=(self.server_address[0],port)
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.bind(server_address)
        sock.settimeout(self.timeoutLimit)        
        tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
        print('invio al client  ' ,filename)
        count=0
        with open(os.path.join(self.path, filename), 'rb') as file:
            chunk= file.read(4096*2)
            while True:
                try:
                    #if random.randint(0, 30)==count:
                    #    time.sleep(10)
                    #    print('perso pacchetto',count)
                    #else:
                    self.send(sock,address,chunk,0,count)
                    data,address,checksum,a,b,c,d = self.rcv(sock)
                    while a is OPType.NACK.value:
                        print('qualche errore è successo pacchetto',count)
                        self.send(sock,address,chunk,0,count)
                        data,address,checksum,a,b,c,d = self.rcv(sock)
                    chunk= file.read(4096*2)
                    print('inviato pacchetto ',count)
                    count+=1
                    if count==tot_packs:
                        print('inviati ',count,' su ',tot_packs)
                        break  
                except sk.timeout:
                    print('timeout pacchetto ',count)
                
        self.send(sock,address,'chiudo la connessione'.encode(),OPType.CLOSE_CONNECTION.value,tot_packs)
        sock.settimeout(None)
        sock.close()
        self.release_port(port)
    
    def download(self,filename,address):
        port=self.occupy_port()
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,address,'invio porta'.encode(),0,port)
        self.sock.settimeout(None)
        server_address=(self.server_address[0],port)
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.bind(server_address)
        sock.settimeout(self.timeoutLimit)
        print('scarico dal client',filename)
        count = 0
        with open(os.path.join(self.path, filename), 'wb') as file:
            while True:
                try:
                    data,address,checksum,a,b,c,d = self.rcv(sock)
                    while d != checksum or count != b:
                        print('qualche errore pacchetto ',count,'ricevuto pacchetto ',b)
                        self.send(sock,address,'nack'.encode(),OPType.NACK.value,count)
                        data,address,checksum,a,b,c,d = self.rcv(sock)
                    if a is OPType.CLOSE_CONNECTION.value :
                        print('arrivati ', count, ' su ', b)
                        sock.settimeout(None)
                        break
                    print('ricevuto pacchetto ',count)
                    self.send(sock,address,'ack'.encode(),OPType.ACK.value,count)
                    file.write(data)
                    count += 1 
                except sk.timeout:
                    print('timeout pacchetto ',count)
                 
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
        while True:
            self.sock.settimeout(None)
            print('aspetto')
            data,address,checksum,a,b,c,d = self.rcv(self.sock)
            if a==OPType.UPLOAD.value:
                #server.upload(data.decode('utf8'),address)
                threading.Thread(target=self.upload, args=(data.decode('utf8'),address,)).start()
            elif a==OPType.GET_SERVER_FILES.value:
                print(address)
                self.get_files(address)
            elif a==OPType.DOWNLOAD.value:
                threading.Thread(target=self.download, args=(data.decode('utf8'),address,)).start()
                #self.download(data.decode('utf8'),address)               
    
if __name__ == '__main__':
     server=Server('10.0.0.2',10000)
     threading.Thread(target=Ui,args=(server,)).start()
         