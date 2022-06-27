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
       self.port=port
       self.server_name=server_address
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
        print('file nel server ' ,listToStr)
        return listToStr
        
    def get_files(self, address):
        self.sock.settimeout(self.timeoutLimit)
        listToStr = ''.join([(str(directory) + '\n') for directory in os.listdir(self.path)])
        print('invio al client  ' ,listToStr)
        self.send(self.sock,address,listToStr.encode(),OPType.GET_SERVER_FILES.value,0)
        self.sock.settimeout(None)
        
    def upload(self,filename,port,file):
        if filename in os.listdir(self.path):
            print ('upload client porta',port)
            sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
            server_address=(self.server_name,port)
            sock.bind(server_address)
            sock.settimeout(self.timeoutLimit)        
            tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
            count=0
            data,address,checksum,a,b,c,d = self.rcv(sock)
            print('invio al client  ' ,filename)
            
            while True:
                try:
                    chunk= file.read(4096*2)
                    #if random.randint(0, 30)==count:
                    #    time.sleep(10)
                    #    print('perso pacchetto',count)
                    #else:
                    #    self.send(sock,address,chunk,0,count)
                    self.send(sock,address,chunk,0,count)
                    data,address,checksum,a,b,c,d = self.rcv(sock)
                    while a is OPType.NACK.value:
                        print('qualche errore è successo pacchetto',count)
                        self.send(sock,address,chunk,0,count)
                        data,address,checksum,a,b,c,d = self.rcv(sock)
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    while True:
                        try:
                            self.send(sock,address,chunk,0,count)
                            data,address,checksum,a,b,c,d = self.rcv(sock)
                            if a is OPType.ACK.value:
                                break
                        except sk.timeout:
                            print('timeout pacchetto ',count)
                print('inviato pacchetto ',count)
                count+=1
                if count==tot_packs:
                    print('inviati ',count,' su ',tot_packs)
                    break  
        else:
            print('non presente  ' ,filename)
        self.send(sock,address,'chiudo la connessione'.encode(),OPType.CLOSE_CONNECTION.value,tot_packs)
        sock.settimeout(None)
    
    def download(self,filename,port):
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        print ('download client porta',port)
        server_address=(self.server_name,port)
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
                except sk.timeout:
                    print('timeout pacchetto ',count)
                    while True:
                        try:
                            self.send(sock,address,'nack'.encode(),OPType.NACK.value,count)
                            data,address,checksum,a,b,c,d = self.rcv(sock)
                            if count==b:
                                break
                        except sk.timeout:
                            print('timeout pacchetto ',count) 
                print('ricevuto pacchetto ',count)
                self.send(sock,address,'ack'.encode(),OPType.ACK.value,count)
                file.write(data)
                count += 1
        sock.settimeout(None)
      
    def start_server(self):
        print ('avvio server')
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        threading.Thread(target=self.server_main_loop).start()
    
    def close_server(self):
        print ('spengo server')
        self.sock.close()
        
    def connect_client(self,address):    
        port=self.occupy_port()
        print ('connessione client porta',port)
        self.sock.settimeout(self.timeoutLimit)
        self.send(self.sock,address,'invio porta'.encode(),0,port)
        self.sock.settimeout(None)
    
    def disconnect_client(self,address):
        print ('disconnetto client')
        self.release_port(address)
    
    def server_main_loop(self):
        while True:
            self.sock.settimeout(None)
            print('aspetto')
            data,address,checksum,a,b,c,d = self.rcv(self.sock)
            if a==OPType.UPLOAD.value:
                #server.upload(data.decode('utf8'),address)
                with open(os.path.join(self.path, data.decode('utf8')), 'rb') as file:
                    threading.Thread(target=self.upload, args=(data.decode('utf8'),b,fiel,)).start()
            elif a==OPType.GET_SERVER_FILES.value:
                self.get_files(address)
            elif a==OPType.DOWNLOAD.value:
                threading.Thread(target=self.download, args=(data.decode('utf8'),b,)).start()
                #self.download(data.decode('utf8'),address)               
            elif a==OPType.CLOSE_CONNECTION.value:  
                self.disconnect_client(b)
            elif a==OPType.BEGIN_CONNECTION.value:  
                self.connect_client(address)
    
if __name__ == '__main__':
     server=Server('10.0.0.20',10000)
     threading.Thread(target=Ui,args=(server,)).start()
         