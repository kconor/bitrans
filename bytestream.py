class bytestream:
    def __init__(self,string):
        self.stream = string

    def __repr__(self):
        return self.stream

    def __str__(self):
        return self.__repr__()

    def read(self, n):
        bytes = self.stream[:2*n]
        self.stream = self.stream[2*n:]
        return bytestream(bytes)

    def peek(self, n):
        return bytestream(self.stream[2*n:])

    def unsigned(self):
        x = int(self.stream, 16)
        rev_x = 0

        nbits = len(self.stream)*4
        # reverse bits
        for i in xrange(nbits):
            if (x & (1 << i)):
                rev_x |= (1 << (nbits - 1 - i))
        return rev_x
        
    def signed(self):
        nbits = len(self.stream)*4
        x = self.unsigned()
        if x > 2**(nbits-1) - 1:
            return -(2**(nbits) - x)
        return x
    
