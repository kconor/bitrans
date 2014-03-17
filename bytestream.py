import math

def fromunsigned(x, nbytes=None):
    if nbytes is None:
        if x == 0:
            nbytes = 1
        else:
            nbytes = int((math.log(x,2) // 8)) + 1
    nbits = nbytes * 8
    rev_x = 0
    for i in xrange(nbits):
        if (x & (1 << i)):
            rev_x |= (1 << (nbits - 1 - i))
    h = hex(rev_x)[2:]
    if len(h) % 2:
        h = '0' + h
    while len(h) < nbytes * 2:
        h = '00' + h
    return bytestream(h)

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
        x = int(self.stream, 16)
        if endian == "little":
            rev_x = 0
            
            nbits = len(self.stream)*4
            # reverse bits
            for i in xrange(nbits):
                if (x & (1 << i)):
                    rev_x |= (1 << (nbits - 1 - i))
            return rev_x
        else:
            return x
        
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

        
            
        
