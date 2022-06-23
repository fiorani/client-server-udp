import zlib
import os

def checksum_calculator(data):
 checksum = zlib.crc32(data)
 return checksum

def return_list_of_files_in(directoryName):
    if not os.path.exists(os.path.join(os.getcwd(), directoryName)):
       os.mkdir(os.path.join(os.getcwd(), directoryName))     
    path = os.path.join(os.getcwd(), directoryName)
    return os.listdir(path)