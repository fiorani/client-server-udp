import socket as sk
from socket import error as sock_err
import time
import struct
import os
import math
import utilities as ut
import threading
from clientMenu import Ui
from operationType import OperationType as OPType
from segmentFactory import SegmentFactory

class Client:

    def __init__(self,server_address,port):
       self.server_address=(server_address,port)
       self.timeoutLimit = 6
       self.buffer=4096*4
       self.perc='0'
       self.sleep=0.01
       self.directoryName='file_client'
       self.state='off'
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
        return ut.get_files_as_string(self.path)
    
    def get_files_from_server(self):
        try:
            self.sock.settimeout(self.timeoutLimit)
            self.send(self.sock,self.server_address,SegmentFactory.getServerFilesRequestSegment())
            data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
            self.sock.settimeout(None)
            if checksum_correct != checksum:
                return 'try again'
            elif data and OPType.GET_SERVER_FILES.value==op:
                return data.decode('utf8')
            else:
                return 'try again'
        except sock_err:
            self.state='error'
            return 'try again'
      
    def upload(self,filename):
        try:
            self.sock.settimeout(self.timeoutLimit)
            print('sending filename to the server: ',filename)
            tot_packs = math.ceil(os.path.getsize(os.path.join(self.path, filename))/(4096*2))
            self.send(self.sock,self.server_address, SegmentFactory.getUploadToServerRequestSegment(filename, tot_packs))
            data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
            port=p
            server_address=(self.server_address[0],port)
            print('address ',server_address)
            count=0
            tries=0
            with open(os.path.join(self.path, filename), 'rb') as file:
                chunk= file.read(4096*2)
                print('sent packet ',count)
                while True:
                    try:
                        self.send(self.sock,server_address,SegmentFactory.getUploadChunkSegment(count, chunk))
                        data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
                        if op==OPType.NACK.value:
                            self.state='error'
                            print('an error occurred on packet',count)
                        elif count==tot_packs:
                            self.perc='100'
                            print('sent ',count,' out of ',tot_packs)
                            break
                        elif op==OPType.ACK.value:
                            chunk= file.read(4096*2)
                            self.perc=str(int((count*100)/tot_packs))
                            count+=1
                            print('sent packet ',count)
                            tries=0
                    except sk.timeout:
                        self.state='timeout'
                        print('packet timeout',count)
                        tries+=1
                        if(tries==5):
                            self.state='failed upload'
                            print('failed upload ')
                            break
            self.send(self.sock,server_address,SegmentFactory.getCloseConnectionSegment())
            self.sock.settimeout(None)
        except sock_err:
            self.state='failed upload'
    
    def download(self,filename):
        try:
            self.sock.settimeout(self.timeoutLimit)
            print('sending filename to the server ',filename)
            self.send(self.sock,self.server_address, SegmentFactory.getDownloadToClientRequestSegment(filename))
            data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
            tot_packs=c
            port=p
            server_address=(self.server_address[0],port)
            print('address ',server_address)
            count = 0
            tries=0
            with open(os.path.join(self.path, filename), 'wb') as file:
                while True:
                    try:
                        data,address,checksum,op,c,p,checksum_correct = self.rcv(self.sock)
                        if op is OPType.CLOSE_CONNECTION.value :
                            count-=1
                            print('arrived ', count, ' out of ', tot_packs)
                            self.sock.settimeout(None)
                            break
                        elif checksum_correct != checksum or count != c:
                            self.state='error'
                            print('an error occurred on packet ',count,'received packet ',count)
                            self.send(self.sock,server_address,SegmentFactory.getNACKSegment(count))
                        else:
                            print('received packet ',count)
                            self.send(self.sock,server_address,SegmentFactory.getACKSegment(count))
                            file.write(data)
                            count += 1
                            self.perc=str(int((count*100)/tot_packs))
                            tries=0
                    except sk.timeout:
                        self.state='timeout'
                        print('timeout packet ',count)
                        self.send(self.sock,server_address,SegmentFactory.getNACKSegment(count))
                        tries+=1
                        if(tries==5):
                            self.state='failed download'
                            print('failed download ')
                            file.close()
                            os.remove(os.path.join(self.path, filename))
                            break
                self.sock.settimeout(None)
        except sock_err:
            os.remove(os.path.join(self.path, filename))
            self.state='failed download'
    
    def status(self):
        return 'procedure state '+self.perc+'% completed client state '+self.state
      
    def start_client(self):
        print('starting client')
        self.state='on'
        self.sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        
        
    def close_client(self):
        try:
            print('closing client')
            self.state='off'
            self.sock.settimeout(None)
            self.sock.close()
        except sock_err:
            self.state='error'
        
if __name__ == '__main__':
    client=Client('localhost',10000)
    threading.Thread(target=Ui,args=(client,)).start()
    