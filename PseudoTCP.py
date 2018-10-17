
from Node import *
from socket import *
from random import *

from ReachabilityTables import *
from SocketPseudoTCP import *
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    GG = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SegmentStructure():
    """docstring for SegmentStructure."""
    def __init__(self, sourcePort,destinationPort,sequenceNumber,acknowledgmentNumber,headerLength,flagACK,flagFIN,flagSYN,data):
        self.sourcePort = sourcePort # 2bytes
        self.destinationPort = destinationPort #2bytes
        self.sequenceNumber = sequenceNumber #4bytes
        self.acknowledgmentNumber = acknowledgmentNumber #4bytes
        self.headerLength = headerLength # 4bits
        self.flagACK = flagACK # 1bit
        self.flagFIN = flagFIN # 1bit
        self.flagSYN = flagSYN # 1bit
        self.noUSE = 1 #1bit
        self.data = data # 8bytes
    def encode(self):

        return 1
    def decode(self, byte_array):
        sourcePort = byte_array[:2]
        destinationPort = byte_array[2:4]
        sequenceNumber = byte_array[4:8]
        acknowledgmentNumber = byte_array[8:12]
        headerLength = byte_array[13]

        return 2

pseudo = PseudoTCP('localhost','8080')
pseudo.clientPseudoTCP('localhost',8080)
