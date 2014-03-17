import re
import os

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
    def __init__(self, s):#sig, pubkey, string):
        #self.sig = bytestream.fromunsigned(sig)
        #self.pubkey = bytestream.bytestream(pubkey)
        if isinstance(s, str):
            self.bstream = bytestream.bytestream(s)
        else:
            self.bstream = s
        self.machine = machine.machine()

    def __add__(self, other):
        return script(self.bstream + other.bstream)

    def interpret(self, animate=False):
        #self.machine.push(self.sig)
        #self.machine.push(self.pubkey)
        if animate:
            self.machine.draw()
        while not self.bstream.isempty():
            code = self.bstream.read(1).unsigned(endian="big")
            op = ops.code[code]
            print op
            op(self.bstream, self.machine)
            if animate:
                self.machine.draw()
        if self.machine.peek().unsigned == 0:
            return False
        return True
            
            
