import copy
import hashlib

import bytestream

class InvalidTransactionException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

# op function implementations
def empty_array(stream, machine):
    empty_array = bytestream("")
    stream.push(empty_array)
    return empty_array

def pusher_maker(i):
    def pusher(stream, machine):
        data = stream.read(i)
        machine.push(data)
        return data
    return pusher

def reader_pusher_maker(i):
    def reader_pusher(stream, machine):
        nbytes = stream.read(i).unsigned()
        data = stream.read(nbytes)
        machine.push(data)
        return data
    return reader_pusher

def numpusher_maker(x):
    def numpusher(stream, machine):
        data = bytestream.fromunsigned(x)
        machine.push(data)
        return data
    return numpusher
        
def toalt(stream, machine):
    data = machine.stack.pop()
    machine.alt.push(data)
    return data

def fromalt(stream, machine):
    data = machine.alt.pop()
    machine.stack.push(data)
    return data

def ifdup(stream, machine):
    data = machine.stack.pop()
    if data.signed() != 0:
        machine.stack.push(copy.deepcopy(data))
    machine.stack.push(data)
    return data

def depth(stream, machine):
    data = len(machine.stack)
    machine.stack.push(data)
    return data

def drop(stream, machine):
    machine.stack.pop()

# should return data and copied data
def dup(stream, machine):
    data = machine.stack.pop()
    machine.push(copy.deepcopy(data))
    machine.push(data)
    return data

def nip(stream, machine):
    data = machine.stack.pop(-2)
    return data

def over(stream, machine):
    data = copy.deepcopy(machine.stack[-2])
    machine.stack.push(data)
    return data

def pick(stream, machine):
    n = stream.read(1).unsigned()
    data = copy.deepcopy(machine.stack[-n])
    machine.stack.push(data)
    return data

def roll(stream, machine):
    n = stream.read(1).unsigned()
    data = machine.stack.pop(-n)
    machine.stack.push(data)
    return data

def rot(stream, machine):
    data = machine.stack.pop(-3)
    machine.stack.push(data)
    return data

def swap(stream, machine):
    data = machine.stack.pop(-2)
    machine.stack.push(data)
    return data

def tuck(stream, machine):
    top = machine.stack.pop()
    middle = machine.stack.pop()
    data = copy.deepcopy(top)
    machine.stack.push(data)
    machine.stack.push(middle)
    machine.stack.push(top)
    return data

def drop2(stream, machine):
    [machine.stack.pop() for i in range(2)]

def dup2(stream, machine):
    i2 = copy.deepcopy(machine.stack[-2])
    i1 = copy.deepcopy(machine.stack[-1])
    machine.stack.push(i2)
    machine.stack.push(i1)
    return i1

def dup3(stream, machine):
    i3 = copy.deepcopy(machine.stack[-3])
    i2 = copy.deepcopy(machine.stack[-2])
    i1 = copy.deepcopy(machine.stack[-1])
    machine.stack.push(i3)
    machine.stack.push(i2)
    machine.stack.push(i1)
    return i1

def hash160(stream, machine):
    import pdb
    pdb.set_trace()
    data = machine.pop()
    sha256 = hashlib.new('sha256')
    ripemd160 = hashlib.new('ripemd160')
    sha256.update(data.stream.decode('hex'))
    ripemd160.update(sha256.digest())
    hashed = bytestream.bytestream(ripemd160.hexdigest())
    machine.push(hashed)
    return bytestream.bytestream(ripemd160.hexdigest())
        
def equal(stream, machine):
    x1 = machine.pop()
    x2 = machine.pop()
    if x1 == x2:
        machine.push(bytestream.fromunsigned(1))
    else:
        machine.push(bytestream.fromunsigned(0))

def verifier_maker(f, msg):
    def verifier(stream, machine):
        f(stream, machine)
        top = machine.peek().unsigned()
        if top == 0:
            raise InvalidTransactionException(msg)
        else:
            machine.pop()
    return verifier

def disabled_maker(msg):
    def disabled(stream, machine):
        raise InvalidTransactionException(msg)
    return disabled
    
