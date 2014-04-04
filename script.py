import re
import os
import copy

import ops
import bytestream
import machine

class script:
    def __init__(self, s):
        if isinstance(s, str):
            self.bstream = bytestream.bytestream(s)
        else:
            self.bstream = s
        self.original_bstream = copy.deepcopy(self.bstream)

    def __add__(self, other):
        return script(self.bstream + other.bstream)

    def __len__(self):
        return len(self.original_bstream)

    def stream(self):
        return copy.deepcopy(self.original_bstream)

    def interpret(self, stack_machine = None, transaction = None, index = None, animate = False):
        if stack_machine is None:
            stack_machine = machine.machine()  # create a clean machine if none provided
        if animate:
            stack_machine.draw()
        while not self.bstream.isempty():
            code = self.bstream.read(1).unsigned(endian="big")
            op = ops.code[code]
            print op
            
            #special cases
            if op.word == "OP_IF" or op.word == "OP_NOTIF":
                top_value = stack_machine.pop()
                if op.word == "OP_IF":
                    consequence = top_value.signed() != 0
                elif op.word == "OP_NOTIF":
                    consequence = top_value.signed() == 0
                if consequence:
                    stack_machine.pushifstate("eval-consequent")
                    continue
                else:
                    stack_machine.pushifstate("ignore-consequent")
                    stack_machine.lock()
                    continue
            elif op.word == "OP_ELSE":
                if not stack_machine.inif():
                    print "OP_ELSE called outside of if statement"
                    return False
                if stack_machine.inifstate("eval-consequent"):
                    stack_machine.changeifstate("ignore-alternative")
                    stack_machine.lock()
                elif stack_machine.inifstate("ignore-consequent"):
                    stack_machine.changeifstate("eval-alternative")
                    stack_machine.unlock()
            elif op.word == "OP_ENDIF":
                if not stack_machine.inif():
                    print "OP_ENDIF called outside of if statement"
                    return False
                if stack_machine.inifstate("ignore-alternative"):
                    stack_machine.unlock()
                stack_machine.popifstate()
            elif op.word == 'OP_CHECKSIG':  #checksig is a special case
                if transaction is None or index is None:
                    print "OP_CHECKSIG called but transaction or index missing; script invalid"
                    return False
                op(self.bstream, stack_machine, transaction, index, self)
            # usual case
            else:
                op(self.bstream, stack_machine)
                
            if animate:
                stack_machine.draw(op)
        
        # reset the stream
        self.bstream = self.stream()
        if stack_machine.peek().unsigned() == 0:
            return False
        return True
            
            
