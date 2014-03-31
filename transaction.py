import bytestream
import script
import machine
import sys

class transaction:
    def __init__(self, txid, server):
        self.server = server
        tx = server("getrawtransaction", txid, 1)
        self.txid = txid
        try:
            stream = bytestream.bytestream(tx['hex'])
        except TypeError as e:
            print "Server returned error. Probably can't find the transaction key."
            print "\tTypeError error: {0}:".format(e)
            sys.exit(1)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        self.version = stream.read(4).unsigned()
        self.tx_in_count = stream.readvarlensize()
        self.tx_in  = [txin(stream) for i in xrange(self.tx_in_count)]
        self.tx_out_count = stream.readvarlensize()
        self.tx_out = [txout(stream) for i in xrange(self.tx_out_count)]
        self.lock_time = stream.read(4).unsigned()

    def verify(self, animate=False):
        valid = True
        for idx,tin in enumerate(self.tx_in):
            # clean machine for each input
            stack_machine = machine.machine()
            # always eval tin
            valid = valid and tin.script.interpret(stack_machine=stack_machine)
            # coinbase transactions do not refer to a previous output, but other transactions do
            if not tin.is_coinbase:
                prev_tran = transaction(tin.prev_hash, self.server)
                tout = prev_tran.tx_out[tin.index]
                valid = valid and tout.script.interpret(stack_machine=stack_machine,  #operate on dirty machine
                                                        transaction=self,
                                                        index=idx,
                                                        animate=animate)  
        return valid

    def encode(self):
        stream = bytestream.bytestream('')
        stream += bytestream.fromunsigned(self.version,4)
        stream += bytestream.fromvarlen(self.tx_in_count)
        for tx_in in self.tx_in:
            stream += tx_in.encode()
        stream += bytestream.fromvarlen(self.tx_out_count)
        for tx_out in self.tx_out:
            stream += tx_out.encode()
        stream += bytestream.fromunsigned(self.lock_time,4)
        return stream

            
class txin:
    def __init__(self, stream):
        self.prev_hash = str(stream.read(32).reverse().stream)
        self.index = stream.read(4).unsigned()
        self.script_length = stream.readvarlensize()
        self.script = script.script(stream.read(self.script_length))
        self.sequence = stream.read(4).unsigned()

        if int(self.prev_hash,16) == 0:
            self.is_coinbase = True
        else:
            self.is_coinbase = False

    def encode(self):
        stream = bytestream.bytestream("")
        stream += bytestream.bytestream(self.prev_hash).reverse()
        stream += bytestream.fromunsigned(self.index,4)
        stream += bytestream.fromvarlen(self.script_length)
        stream += self.script.stream()
        stream += bytestream.fromunsigned(self.sequence,4)
        return stream

class txout:
    def __init__(self, stream):
        self.value = stream.read(8).unsigned()
        self.script_length = stream.readvarlensize()
        self.script = script.script(stream.read(self.script_length))

    def encode(self):
        stream = bytestream.bytestream("")
        stream += bytestream.fromunsigned(self.value,8)
        stream += bytestream.fromvarlen(self.script_length)
        stream += self.script.stream()
        return stream
