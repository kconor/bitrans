import math

def fromunsigned(x, nbytes = None):
    if nbytes is None:
        if x == 0:
            nbytes = 1
        else:
            nbytes = int((math.log(x,2) // 8)) + 1
    hx = hex(x)[2:]
    if type(x) == long:
        hx = hx[:-1]
    if len(hx) % 2:
        hx = '0' + hx
    while len(hx) < nbytes * 2:
        hx = '00' + hx
    return bytestream((hx.decode('hex')[::-1]).encode('hex'))

def fromvarlen(x):
    if x < 0xfd:
        return fromunsigned(x,1)
    elif x <= 0xffff:
        return bytestream('fd') + fromunsigned(x,2)
    elif x <= 0xfffffff:
        return bytestream('fe') + fromunsigned(x,4)
    else:
        return bytestream('ff') + fromunsigned(x,8)
    

class bytestream:
    def __init__(self,string):
        self.stream = string
    
    def __repr__(self):
        return self.stream

    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        return bytestream(self.stream + other.stream)

    def __eq__(self, other):
        return self.stream == other.stream

    def __len__(self):
        """
        Returns length in bytes. Since hex representation is 4 bits
        """
        return len(self.stream) / 2

    def reverse(self):
        bits = self.stream.decode('hex_codec')
        return bytestream(bits[::-1].encode('hex'))
        
    def read(self, n):
        bytes = self.stream[:2*n]
        self.stream = self.stream[2*n:]
        return bytestream(bytes)

    def peek(self, n, interval=None):
        if interval is None:
            return bytestream(self.stream[:2*n])
        return bytestream(self.stream[2*n:2*(n+interval)])

    def isempty(self):
        return len(self.stream) < 1

    def unsigned(self,endian="little"):
        if endian == "little":
            return int((self.stream.decode('hex_codec')[::-1]).encode('hex'),16)
        else:
            return int(self.stream, 16)
        
    def signed(self,endian="little"):
        nbits = len(self.stream)*4
        x = self.unsigned(endian)
        if x > 2**(nbits-1) - 1:
            return -(2**(nbits) - x)
        return x

    def peekvarlensize(self):
        val = self.peek(1).unsigned(endian='big')
        if val < 0xfd:
            return (1,val)
        val = self.peek(2).unsigned(endian='big')
        if val <= 0xffff:
            return (3,self.peek(1,2).unsigned(endian='big'))
        val = self.peek(4).unsigned(endian='big')
        if val <= 0xffffffff:
            return (5,self.peek(1,4).unsigned(endian='big'))
        else:
            return (9,self.peek(1,8).unsigned(endian='big'))

    def readvarlensize(self):
        size = self.peekvarlensize()
        self.read(size[0])
        return size[1]

        
            
        
