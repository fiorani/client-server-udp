# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 17:15:35 2022

@author: pnmat
"""

import struct 
from operationType import OperationType as OPType
import utilities as ut

class SegmentFactory:
    
    def getListOfFilesSegment(files):
        return struct.pack("!IIII", OPType.GET_SERVER_FILES, 0, 0, ut.checksum_calculator(files.encode())) + files.encode()
    
    def getFileRequestSegment():
        return struct.pack("!IIII", OPType.GET_SERVER_FILES, 0, 0, 0)
     
    def getBeginConnectionSegment(port, tot_frames):
        return struct.pack("!IIII", OPType.BEGIN_CONNECTION.value, port, tot_frames, 0)
    
    def getUploadFrameSegment(seqNumber, frame):
        return struct.pack("!IIII", OPType.UPLOAD.value, 0, seqNumber, ut.checksum_calculator(frame.encode())) + frame.encode()
    
    def getDownloadRequestSegment(filename):
        return struct.pack("!IIII", OPType.DOWNLOAD.value, 0, 0, ut.checksum_calculator(filename.encode())) + filename.encode()
        
    def getACKSegment(seqNumber):
        return struct.pack("!IIII", OPType.ACK.value, 0, seqNumber, 0)
    
    def getNACKSegment(seqNumber):
        return struct.pack("!IIII", OPType.NACK.value, 0, seqNumber, 0)
    
    def getCloseConnectionSegment():
        return struct.pack("!IIII", OPType.CLOSE_CONNECTION.value, 0, 0, 0)
    