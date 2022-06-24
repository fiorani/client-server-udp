# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 09:58:39 2022

@author: pnmat
"""

import enum

class OperationType(enum.Enum):
    BEGIN_CONNECTION = 1
    DOWNLOAD = 2
    UPLOAD = 3
    ACK = 4
    NACK = 5
    CLOSE_CONNECTION = 6
    