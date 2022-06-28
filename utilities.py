import zlib
import os

def checksum_calculator(data):
 checksum = zlib.crc32(data)
 return checksum

def create_directory(directoryName):
    if not os.path.exists(os.path.join(os.getcwd(), directoryName)):
       os.mkdir(os.path.join(os.getcwd(), directoryName))     

def return_list_of_files_in(directoryName):
    return os.listdir(os.path.join(os.getcwd(), directoryName))