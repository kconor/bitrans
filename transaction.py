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
            prev_tran = transaction(tin.prev_hash, self.server)
            tout = prev_tran.tx_out[tin.index]
            combined_script = tin.script + tout.script
            valid = valid and combined_script.interpret(animate=animate)
        return valid
            
            
class txin:
    def __init__(self, stream):
        self.prev_hash = str(stream.read(32).reverse().stream)
        self.index = stream.read(4).unsigned()
        self.script_length = stream.readvarlensize()
        self.script = script.script(stream.read(self.script_length))
        self.sequence = stream.read(4).unsigned()

class txout:
    def __init__(self, stream):
        self.value = stream.read(8).unsigned()
        self.script_length = stream.readvarlensize()
        self.script = script.script(stream.read(self.script_length))
