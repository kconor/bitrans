import copy
import hashlib
import ecdsa
import math
import btct

import bytestream
import script

class InvalidTransactionException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


###### Flow Control #########

def nop(stream, machine):
    pass


def op_if(stream, machine):
    data = machine.stack.pop()
    assert type(data) == int
    if data != 0:  # execute statement
        pass

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


def over2(stream, machine):
    i1 = copy.deepcopy(machine.peek[-4])
    i2 = copy.deepcopy((machine.peek[-3]))

    machine.push(i1)
    machine.push(i2)


def rot2(stream, machine):
    i1 = machine.pop(-6)
    i2 = machine.pop(-5)

    machine.push(i1)
    machine.push(i2)


def swap2(stream, machine):
    i1 = machine.pop(-4)
    i2 = machine.pop(-3)

    machine.push(i1)
    machine.push(i2)


#TODO please double check (tian)
def opt_size(stream, machine):
    top_element = machine.peek() # hex value
    if top_element[2:] == '\\x':
        hex_value = top_element[2:]  # get ride of \x
    else:
        hex_value = top_element
    string_top_element = ''.join([chr(int(s, 16))
                                  for s in [hex_value[i: i+2] for i in range(0, len(hex_value), 2)]])
    size_top = len(string_top_element)
    machine.push(bytestream.bytestream(hex(size_top)))  # push hex representation of size_top


######## Arithmetic ops #############

def op_add1(stream, machine):
    top_element = machine.pop()
    if top_element[2:] == '\\x':
        hex_value = top_element[2:]  # get ride of \x
    else:
        hex_value = top_element
    top_stream = bytestream.bytestream(hex_value)

    if len(top_stream) > 4:  # input is longer than 4 bytes
        raise InvalidTransactionException('Integer longer than 4 bytes')

    machine.push(bytestream.bytestream(hex(top_stream.unsigned()+1)))  #TODO verify little or big


def hash160(stream, machine):
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

# this breaks the usual interface; added a special case to the
# interpreter
def checksig(stream, machine, transaction, index, subscript):
    """
    For details, please see https://en.bitcoin.it/wiki/OP_CHECKSIG.
    """
    
    # How it works
    # Firstly always this (the default) procedure is
    # applied: Signature verification process of the default procedure
    # the public key and the signature are popped from the stack, in
    # that order. If the hash-type value is 0, then it is replaced by
    # the last_byte of the signature. Then the last byte of the
    # signature is always deleted.
    pubkey = machine.pop()
    sig = machine.pop()
    #sig.stream = sig.stream[:-2]  # this is actually done later
    
    # A new subscript is created from the instruction from the most
    # recently parsed OP_CODESEPARATOR (last one in script) to the end
    # of the script. If there is no OP_CODESEPARATOR the entire script
    # becomes the subscript (hereby referred to as subScript)
    #  not implemented yet (james)

    # The sig is deleted from subScript.
    #  note: this is nonstandard so I am ignoring it (james)
    
    # All OP_CODESEPARATORS are removed from subScript
    #  not implemented yet (james)

    # The hashtype is removed from the last byte of the sig and stored (as 4 bytes)
    hashtype = bytestream.fromunsigned(bytestream.bytestream(sig.stream[-2:]).unsigned(),4)
    sig.stream = sig.stream[:-2]
    
    # A copy is made of the current transaction (hereby referred to txCopy)
    txCopy = copy.deepcopy(transaction)
    
    # The scripts for all transaction inputs in txCopy are set to empty scripts (exactly 1 byte 0x00)
    for i in xrange(txCopy.tx_in_count):
        txCopy.tx_in[i].script_length = 0
        txCopy.tx_in[i].script = script.script(bytestream.fromunsigned(0,1))
    
    # The script for the current transaction input in txCopy is set to subScript (lead in by its length as a var-integer encoded!)
    txCopy.tx_in[index-1].script_length = len(subscript)
    txCopy.tx_in[index-1].script = subscript
    
    # Serialize txCopy and append hashtype
    serial = txCopy.encode() + hashtype

    # hash twice with sha256
    msg = ((hashlib.sha256(hashlib.sha256(serial.stream.decode('hex')).digest()).digest()))# [::-1]).encode('hex_codec')

    # verify via ecdsa
    key = btct.decompress(pubkey.stream)
    vk = ecdsa.VerifyingKey.from_string(key[2:].decode('hex'), curve=ecdsa.SECP256k1)
    try:
        vk.verify_digest(sig.stream.decode('hex'), msg, sigdecode=ecdsa.util.sigdecode_der)
        machine.push(bytestream.fromunsigned(1,1))
    except ecdsa.BadSignatureError:
        machine.push(bytestream.fromunsigned(0,1))
    
