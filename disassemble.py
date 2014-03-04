import struct

import byte
import ops

#def scan_file(filename):
#    """
#    Read a file of Bitcoin script into a list of ints.
#
#    """
#    f = open(filename,'rb')
#    bytelist = []
#    byte_raw = f.read(1)  #read a byte
#    while byte_raw != "":
#        #interpret the byte as a signed little-endian int
#        byte_num = struct.unpack('b<',opcode_raw) 
#        bytelist.append(byte_num)
#
#        #read another byte
#        byte_raw = f.read(1)
#
#    return bytelist

def scan_hexstring(hexstring):
    """
    Read a hexstring of the form 'A0B102'

    """
    bytelist = []
    for i in xrange(len(hexstring)/2):
        a_byte = byte.byte(hexstring[2*i:2*(i+1)])
        bytelist.append(a_byte)

    return bytelist
    
def parse(hexstring):
    program = []
    bytes = scan_hexstring(hexstring)

    print bytes
    
    while bytes:
        a_byte = bytes[0]
        print byte
        op = ops.code[a_byte.unsigned]
        program.append(op)
        nargs = op.nargs(bytes[1:])
        args = bytes[1:nargs+1]
        program.append(args)
        bytes = bytes[(nargs+1):]
        print "%s %d: %s" % (op, nargs, args)
    return program
