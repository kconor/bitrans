#!/usr/bin/env python
import psycopg2
import binascii
from psycopg2.extras import NamedTupleCursor

import bytestream
import machine
import script

some_hashes = [
    '\\x44eaf56722d9ce7120bccb83a355f038baee72486e964f2b4ac57ac8e32cb1b4',
    '\\x6c01458a6460139d1c104e0a454bfcf5fd77a03a74c8448f8a103920692372fb',
    '\\x6a765ebefb7a72a20f929dcd4773835f914d0bd57e0f18a7f400a21d575e38be',
    '\\x5a51fe08099039b5659713ea1525208c018caa3bc223f1fef5dec57f96abf39e',
    '\\x9c48d9d1483504f423550dc64fac8146a47ebeadc7e39927113cf9c1892566f8',
    '\\x2c391c461530773f2268175f1d74a517b21f1d996403e445374b43fcd1bf385f',
    '\\x7cfc9bf4b91f65faa785eb74939349196a97e5f5654a86b0debe1d61af425a71',
    '\\x2c4c4e7b6c7d9f780a32a2ee85a9e9a1e5be818b85b0d98bac397d69cf59142a',
    '\\x820a3b3cc7d4b74b2ce980670720d7c45e571cbeb451dcd11e39d042f2b331d8',
    '\\x9b0c8d25d31626cabdd4e5dd6587fb592d67d0d5fd5a85974a9096ef0a99e717'
]

class Counts(object):
    def __init__(self):
        self.counts = {}

    def add(self, key):
        val = self.counts.get(key, None)
        if val is not None:
            self.counts[key] = self.counts[key] + 1
        else:
            self.counts[key] = 1

    def prn(self):
        items = sorted(self.counts.items(), key=lambda item: -1 * item[1])
        print("size | count")
        for item in items:
            print("%s | %s" % (str(item[0]).rjust(4), str(item[1]).rjust(5)))


def bytea_to_hex(sig):
    return binascii.hexlify(bytes(sig))


class TxIn(object):
    def __init__(self, tuple):
        #self.prev_hash = bytea_to_hex(tuple.pubkey_hash)
        #print("prev hash: " + self.prev_hash)
        self.txout_id = tuple.txout_id
        self.index = int(tuple.txin_pos)
        tmp_script = bytea_to_hex(tuple.txin_scriptsig)
        self.script_length = len(tmp_script) / 2
        self.script = script.script(tmp_script)
        self.sequence = int(tuple.txin_sequence)
        self.tx_out = TxOut(tuple)
        self.prev_hash = bytea_to_hex(tuple.prev_hash)

        if not self.txout_id:#KC
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

    def prev_out(self):
        return self.tx_out

class TxOut(object):
    def __init__(self, tuple):
        self.value = int(tuple.txout_value)
        tmp_script = bytea_to_hex(tuple.txout_scriptpubkey)
        self.script_length = len(tmp_script) / 2
        self.script = script.script(tmp_script)

    def encode(self):
        stream = bytestream.bytestream("")
        stream += bytestream.fromunsigned(self.value,8)
        stream += bytestream.fromvarlen(self.script_length)
        stream += self.script.stream()
        return stream


class Txn(object):
    def __init__(self, hash, conn):
        self.conn = conn
        self.tx_in = []
        self.tx_out = []
        with self.conn.cursor() as curs:
            #get tx_id, version, and lock time from hash
            sql = curs.mogrify("SELECT tx_id, tx_version, tx_locktime "\
                               "FROM tx WHERE tx_hash=%s", (hash,))
            curs.execute(sql)
            rs = curs.fetchall()
            tx_id = rs[0].tx_id
            self.version = int(rs[0].tx_version)
            self.lock_time = int(rs[0].tx_locktime)
            #load tx_in from tx_id
            sql = "SELECT txin.tx_id, txin.txin_pos, txin.txin_scriptsig, "\
                  "txin.txin_sequence, txin.txout_id, txout.txout_value, "\
                  "txout.txout_scriptpubkey, tx.tx_hash as prev_hash "\
                  "FROM txin, txout, tx "\
                  "WHERE txin.txout_id=txout.txout_id "\
                        "and txin.tx_id=%s "\
                        "and tx.tx_id=txout.tx_id" % tx_id
            curs.execute(sql)
            rs = curs.fetchall()
            for tuple in rs:
                print(tuple)
                self.tx_in.append(TxIn(tuple))
            print("CREATED TXN FOR %s" % tx_id)

    def encode(self):
        stream = bytestream.bytestream('')
        stream += bytestream.fromunsigned(self.version,4)
        stream += bytestream.fromvarlen(self.tx_in_count)
        for tx_in in self.tx_in:
            stream += tx_in.encode()
        stream += bytestream.fromvarlen(self.tx_out_count)
        for txout in self.tx_out:
            stream += txout.encode()
        stream += bytestream.fromunsigned(self.lock_time, 4)
        return stream
    
    @property
    def tx_out_count(self):
        return -1#TODO

    @property
    def tx_in_count(self):
        return len(self.tx_in)


    def verify(self):
        valid = True
        for tin in self.tx_in:
            stack_machine = machine.machine()
            valid = valid and tin.script.interpret(stack_machine=stack_machine)
            if not tin.is_coinbase:
                #prev_txn = tin.prev_txn()
                #tout = prev_txn.tx_out[tin.index]
                tout = tin.prev_out()
                valid = valid and tout.script.interpret(stack_machine=stack_machine,                                                          
                                                        transaction=self,
                                                        index=tin.index)
        return valid


if __name__ == '__main__':
    with psycopg2.connect("dbname=postgres", cursor_factory=NamedTupleCursor) as conn:
        for hash in some_hashes:
            txn = Txn(hash, conn)
            txn.verify()
