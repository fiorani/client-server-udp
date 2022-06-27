#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 16:41:36 2022

@author: panini
"""
import struct 
class Header():
    def __init__(self):
        self.resetHeader()
        
    def resetHeader(self):
        self.operationType = None
        self.seqenceNumber = None
        self.checksum = None
        self.payload = None
    
    def set_operationType(self, opType):
        self.operationType = opType
        
    def set_sequenceNumber(self, seqNum):
        self.seqenceNumber = seqNum
        
    def set_checksum(self, checksum):
        self.checksum = checksum
    
    def set_payload(self, payload):
        self.payload = payload
        
    def build_header(self):
        return struct.pack("!IIII", self.operationType, self.sequenceNumber, self.checksum, self.payload)