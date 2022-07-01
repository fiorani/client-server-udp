import socket as sk
from socket import error as sock_err
import time
import struct
import os
import math
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
       self.sleep=0.01
       self.state=''
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
        return ut.get_files_as_string(self.path)
        
    def get_files(self, address):
        try:
            self.sock.settimeout(self.timeoutLimit)
            print('sending to client  ' ,self.get_self_files())
            self.send(self.sock,address,SegmentFactory.getServerFilesSegment(self.get_self_files()))
            self.sock.settimeout(None)
        except sock_err:
            print('failed get files ')
            self.state='error'
        
    def upload(self,filename,address):
        try:
            port=self.occupy_port()
            tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
            self.sock.settimeout(self.timeoutLimit)
            self.send(self.sock,address, SegmentFactory.getBeginConnectionSegment(port, tot_packs))
            self.sock.settimeout(None)
            server_address=(self.server_address[0],port)
            sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
            sock.bind(server_address)
            sock.settimeout(self.timeoutLimit)        
            print('sending to client  ' ,filename)
            count=0
            tries=0
            file= open(os.path.join(self.path, filename), 'rb')
            chunk= file.read(4096*2)
            print('sent packet ',count)
            while True:
                try:
                    #if random.randint(0, 30)==count:
                    #    time.sleep(10)
                    #    print('perso pacchetto',count)
                    #else:
                    self.send(sock,address,SegmentFactory.getUploadChunkSegment(count, chunk))
                    data,address,checksum,op,c,p,checksum_correct = self.rcv(sock)
                    if op==OPType.NACK.value:
                        print('an error occurred on packet ',count)
                    elif count==tot_packs:
                        print('sent ',count,' out of ',tot_packs)
                        break  
                    elif op==OPType.ACK.value:
                        chunk= file.read(4096*2)
                        count+=1
                        print('sent packet ',count)
                        tries=0
                except sk.timeout:
                    print('timeout packet ',count)
                    self.state='timeout'
                    tries+=1
                    if(tries==5):
                        print('failed upload ')
                        self.state='failed upload'
                        break
        except sock_err:
            print('failed upload ')
            self.state='failed upload'
        finally:
            self.send(sock,address,SegmentFactory.getCloseConnectionSegment())
            file.close()
            sock.settimeout(None)
            sock.close()
            self.release_port(port)
    
    def download(self,filename,address,tot_packs):
        try:
            port=self.occupy_port()
            self.sock.settimeout(self.timeoutLimit)
            self.send(self.sock,address,SegmentFactory.getBeginConnectionSegment(port, 0))
            self.sock.settimeout(None)
            server_address=(self.server_address[0],port)
            sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
            sock.bind(server_address)
            sock.settimeout(self.timeoutLimit)
            print('downloading from client ',filename)
            count = 0
            tries=0
            file= open(os.path.join(self.path, filename), 'wb')
            while True:
                try:
                    data,address,checksum,op,c,p,checksum_correct = self.rcv(sock)
                    if op is OPType.CLOSE_CONNECTION.value :
                        count-=1
                        print('arrived ', count, ' out of ', tot_packs)
                        sock.settimeout(None)
                        break
                    elif checksum_correct != checksum or count != c:
                        if c<count:
                            self.send(sock,address,SegmentFactory.getACKSegment(count))
                        else:
                            print('an error occurred on packet ',count,'received packet ',c)
                            self.send(sock,address, SegmentFactory.getNACKSegment(count))
                    else:
                        print('received packet ',count)
                        self.send(sock,address,SegmentFactory.getACKSegment(count))
                        file.write(data)
                        count += 1 
                        tries=0
                except sk.timeout:
                    print('timeout packet ',count)
                    self.state='timeout'
                    self.send(sock,address, SegmentFactory.getNACKSegment(count))
                    tries+=1
                    if(tries==5):
                        print('failed download ')
                        self.state='failed download'
                        file.close()
                        os.remove(os.path.join(self.path, filename))
                        break
            file.close()
        except sock_err:
            file.close()
            os.remove(os.path.join(self.path, filename))
            print('failed download ')
            self.state='failed download'
        finally:
            sock.settimeout(None)
            sock.close()
            self.release_port(port)
      
    def status(self):
        return 'server state '+self.state
    
    def start_server(self):
        try:
            print ('starting socket')
            self.state='starting server' 
            self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
            self.sock.bind(self.server_address)
            threading.Thread(target=self.server_main_loop).start()
        except sock_err:
             self.state='error'  
    
    def close_server(self):
        try:
            print ('closing socket')
            self.state='closing server' 
            self.sock.settimeout(None)
            self.sock.close()
        except sock_err:
             self.state='error'  
    
    def server_main_loop(self):
        try:
            while True:    
                self.sock.settimeout(None)
                print('waiting')
                data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
                if op==OPType.UPLOAD.value:
                    threading.Thread(target=self.download, args=(data.decode('utf8'),address,c,)).start()
                elif op==OPType.DOWNLOAD.value:
                    threading.Thread(target=self.upload, args=(data.decode('utf8'),address,)).start()
                elif op==OPType.GET_SERVER_FILES.value:
                    threading.Thread(target=self.get_files, args=(address,)).start()
                    #self.get_files(address)
        except sock_err:
            self.state='error'    
    
if __name__ == '__main__':
     server=Server('localhost',10000)
     threading.Thread(target=Ui,args=(server,)).start()
         