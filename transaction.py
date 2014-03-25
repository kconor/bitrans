import bytestream
import script
import machine

class transaction:
    def __init__(self, txid, server):
        self.server = server
        tx = server("getrawtransaction", txid, 1)
        self.txid = txid
        stream = bytestream.bytestream(tx['hex'])
        self.version = stream.read(4).unsigned()
        self.tx_in_count = stream.readvarlensize()
        self.tx_in  = [txin(stream) for i in xrange(self.tx_in_count)]
        self.tx_out_count = stream.readvarlensize()
        self.tx_out = [txout(stream) for i in xrange(self.tx_out_count)]
        self.lock_time = stream.read(4).unsigned()

    def verify(self, animate=False):
        valid = True
        for tin in self.tx_in:
            # coinbase transactions do not refer to a previous output
            if tin.is_coinbase:
                combined_script = tin.script
            # but other transactions do
            else:
                prev_tran = transaction(tin.prev_hash, self.server)
                tout = prev_tran.tx_out[tin.index]
                combined_script = tin.script + tout.script
            valid = valid and combined_script.interpret(self, tin.index, animate=animate)
        return valid

    def encode(self):
        stream = bytestream.bytestream('')
        stream += bytestream.fromunsigned(self.version)
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
