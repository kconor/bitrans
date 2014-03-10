import re

import ops
import bytestream
import machine

url_regex  = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class script:
    def __init__(self, string):#sig, pubkey, string):
        #self.sig = bytestream.fromunsigned(sig)
        #self.pubkey = bytestream.bytestream(pubkey)
        self.bstream = bytestream.bytestream(string)
        self.machine = machine.machine()

    def interpret(self):
        #self.machine.push(self.sig)
        #self.machine.push(self.pubkey)
        while not self.bstream.isempty():
            code = self.bstream.read(1).unsigned(endian="big")
            print code
            op = ops.code[code]
            print op
            op(self.bstream, self.machine)
            
            
