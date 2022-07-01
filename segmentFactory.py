import struct 
from operationType import OperationType as OPType
import utilities as ut

class SegmentFactory:
    
    #Builds a segment used by the server to share its files with the client
    def getServerFilesSegment(files):
        return struct.pack("!IIII", OPType.GET_SERVER_FILES.value, 0, 0, ut.checksum_calculator(files.encode())) + files.encode()
    
    #Builds a segment used by the client to request the list of files stored on the server
    def getServerFilesRequestSegment():
        return struct.pack("!IIII", OPType.GET_SERVER_FILES.value, 0, 0, 0)
     
    #Builds a segment used by the server to initialize a connection with a client on a specific socket
    def getBeginConnectionSegment(port, tot_frames):
        return struct.pack("!IIII", OPType.BEGIN_CONNECTION.value, port, tot_frames, 0)
    
    #Builds a segment used by the client to request an upload of a file to the server
    def getUploadToServerRequestSegment(filename, tot_frames):
        return struct.pack("!IIII", OPType.UPLOAD.value, 0, tot_frames, ut.checksum_calculator(filename.encode())) + filename.encode()
    
    #Builds a segment containing a chunk  
    def getUploadChunkSegment(seqNumber, chunk):
        return struct.pack("!IIII", OPType.UPLOAD.value, 0, seqNumber, ut.checksum_calculator(chunk)) + chunk

    #Builds a segment used by client to request the server to download a file 
    def getDownloadToClientRequestSegment(filename):
        return struct.pack("!IIII", OPType.DOWNLOAD.value, 0, 0, ut.checksum_calculator(filename.encode())) + filename.encode()

    #Builds an ACK segment
    def getACKSegment(seqNumber):
        return struct.pack("!IIII", OPType.ACK.value, 0, seqNumber, 0)
    
    #Builds a NACK segment
    def getNACKSegment(seqNumber):
        return struct.pack("!IIII", OPType.NACK.value, 0, seqNumber, 0)
    
    #Builds a segment used to close a connection
    def getCloseConnectionSegment():
        return struct.pack("!IIII", OPType.CLOSE_CONNECTION.value, 0, 0, 0)
    