# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 09:58:39 2022

@author: pnmat
"""

import enum

class OperationType(enum.IntEnum):
    BEGIN_CONNECTION = 1
    GET_SERVER_FILES = 2
    DOWNLOAD = 3
    UPLOAD = 4
    ACK = 5
    NACK = 6
    CLOSE_CONNECTION = 7
    