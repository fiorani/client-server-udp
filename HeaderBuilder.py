#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 16:22:02 2022

@author: panini
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from header import Header
import struct
from operationType import OperationType as OPType
import utilities as ut

class AbstractHeaderBuilder(ABC):
    "classe astratta che definisce i metodi da richiamare per costruire l'header"
    
    @property
    @abstractmethod
    def create(self):
        pass
    
    
    @abstractmethod
    def setOperationType(self):
        pass
    
    @abstractmethod
    def setSequenceNumber(self):
        pass
    
    @abstractmethod
    def setChecksum(self):
        pass
    
    @abstractmethod
    def setOPayload(self):
        pass
    
    
class BeginConnectionHeaderBuilder(AbstractHeaderBuilder):
        
    def __init__(self):
        self.header = Header()
        self.header.set_operationType(OPType.BEGIN_CONNECTION.value)
        self.header.set_sequenceNumber(None)
        text = "Inizio connessione..."
        self.header.set_checksum(ut.checksum_calculator(text))
        self.header.set_payload(text)
        
    @property
    def create(self):
        header = self.header
        self.header.resetHeader()
        return header.build_header()
        
      
class GetServerFilesHeaderBuilder(AbstractHeaderBuilder):
    
    def __init__(self):
        self.header = Header()
        self.header.set_operationType(OPType.GET_SERVER_FILES.value)
        self.header.set_sequenceNumber(None)
        
        
    @property
    def create(self):
        header = self.header
        self.header.resetHeader()
        return struct.pack("!IIII", header.operationType, header.seqenceNumber, header.checksum, header.payload)
    
    
    def set_checksum(self):
        #self.header.set_checksum(ut.checksum_calculator(self.header.))
        
    def set_payload(self, payload):
        self.header.set_payload(payload)
          