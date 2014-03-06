
def uleb(bytestring):
    """
    uleb -> interpret a bytestring as an unsigned little endian byte

    00 -> 0
    FF -> 255
    10 -> 1
    EF -> 254
    20 -> 2
    A0 -> 10
    6F -> 246
    """
    ordered = bytestring[::-1]
    unsigned = int(ordered,16)
    return unsigned

def sleb(bytestring):
    """
    sleb -> interpret a bytestring as a signed little endian byte

    00 -> 0
    FF -> -1
    10 -> 1
    EF -> -2
    20 -> 2
    A0 -> 10
    6F -> -10
    """
    
    ordered = bytestring[::-1]
    unsigned = int(ordered,16)
    if unsigned > 127:
        return -(256 - unsigned)
    return unsigned

    
def signify(unsigned):
    if unsigned > 127:
        return -(256 - unsigned)
    return unsigned

class byte:
    def __init__(self, hexstring):
        assert(len(hexstring) == 2)
        self.unsigned = uleb(hexstring)
        if self.unsigned > 127:
            self.signed = -(256 - self.unsigned)
        else:
            self.signed = self.unsigned

    def __repr__(self):
        return str(self.unsigned)

    def __str__(self):
        return self.__repr__()
            
        
