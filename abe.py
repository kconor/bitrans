#!/usr/bin/env python
import psycopg2
import binascii
from psycopg2.extras import NamedTupleCursor

import transaction
import bytestream
import machine
import script
import rpc

#failed hashes on rpc
#\x7b1abe989a92e2e667ad57c7006629080bcefb5d4bc4afa414bcb2565423ab9a
#\x69b9703cae493965d6ef51b61d2aa78173c693e8b483c185072b50161bfb167f


some_hashes = [
    '\\x6632b2656832f20a411b53ac6f7923404193308b6c09e3dd4e5a0f9fac4c33d6',
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
    def __init__(self, tuple, txn):
        #self.prev_hash = bytea_to_hex(tuple.pubkey_hash)
        #print("prev hash: " + self.prev_hash)
        self.txout_id = tuple.txout_id
        self.index = int(tuple.txin_pos)
        tmp_script = bytea_to_hex(tuple.txin_scriptsig)
        self.script_length = len(tmp_script) / 2
        self.script = script.script(tmp_script)
        self.sequence = int(tuple.txin_sequence)
        self.tx_out = TxOut(tuple)
        txn.tx_out.append(self.tx_out)
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
                self.tx_in.append(TxIn(tuple, self))

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
        return len(self.tx_out)

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


def show_encoding(txn1, txn2):
    if not (bytestream.fromunsigned(txn1.version, 4) == 
            bytestream.fromunsigned(txn2.version, 4)):
        print(bytestream.fromunsigned(txn.version, 4))
    else:
        print("version ok")
    if not (bytestream.fromvarlen(txn1.tx_in_count) ==  
            bytestream.fromvarlen(txn2.tx_in_count)):
        print(bytestream.fromvarlen(txn.tx_in_count))
    else:
        print("tx_in_count ok")

    for i,(tx_in1,tx_in2) in enumerate(zip(txn1.tx_in,txn2.tx_in)):
        print(" compare tx_in %s" % i)
        if not (bytestream.bytestream(tx_in1.prev_hash).reverse() == 
                bytestream.bytestream(tx_in2.prev_hash).reverse()):
            print("  BAD tx_in.prev_hash")
            print("   " + str(bytestream.bytestream(tx_in1.prev_hash).reverse()))
            print("   " + str(bytestream.bytestream(tx_in2.prev_hash).reverse()))
        else:
            print("  tx_in.prev_hash ok")
        if not (bytestream.fromunsigned(tx_in1.index, 4) == 
                bytestream.fromunsigned(tx_in2.index, 4)):
            print("  BAD tx_in.index")
            print("   " + str(bytestream.fromunsigned(tx_in1.index, 4)))
            print("   " + str(bytestream.fromunsigned(tx_in2.index, 4)))
        else:
            print("  tx_in.index ok")
            print("   " + str(bytestream.fromunsigned(tx_in1.index, 4)))
            print("   " + str(bytestream.fromunsigned(tx_in2.index, 4)))
        if not (bytestream.fromvarlen(tx_in1.script_length) == 
                bytestream.fromvarlen(tx_in2.script_length)):
            print("  BAD tx_in.script_length")
            print("   " + str(bytestream.fromvarlen(tx_in1.script_length)))
            print("   " + str(bytestream.fromvarlen(tx_in2.script_length)))
        else:
            print("  tx_in.script_length ok")
        if not tx_in1.script.stream() == tx_in2.script.stream():
            print("  BAD tx_in.script")
            print("   " + str(tx_in1.script.stream()))
            print("   " + str(tx_in2.script.stream()))
        else:
            print("  tx_in.script ok")
        if not (bytestream.fromunsigned(tx_in1.sequence, 4) == 
                bytestream.fromunsigned(tx_in2.sequence, 4)):
            print("  BAD tx_in.sequence")
            print("   " + str(bytestream.fromunsigned(tx_in1.sequence, 4)))
            print("   " + str(bytestream.fromunsigned(tx_in2.sequence, 4)))
        else:
            print("  tx_in.sequence ok")
    if not (bytestream.fromvarlen(txn1.tx_out_count) == 
            bytestream.fromvarlen(txn2.tx_out_count)):
        print("  BAD txn.tx_out_count")
        print("   " + str(bytestream.fromvarlen(txn1.tx_out_count)))
        print("   " + str(bytestream.fromvarlen(txn2.tx_out_count)))
    else:
        print("tx_out_count ok")
    for i,(txout1,txout2) in enumerate(zip(txn1.tx_out,txn2.tx_out)):
        print(" compare tx_out %s" % i)
        if not (bytestream.fromunsigned(txout1.value, 8) == 
                bytestream.fromunsigned(txout2.value, 8)):
            print("  BAD tx_out.value")
            print("   " + str(bytestream.fromunsigned(txout1.value, 8)))
            print("   " + str(bytestream.fromunsigned(txout2.value, 8)))
        else:
            print("  tx_out.value ok")
        if not (bytestream.fromvarlen(txout1.script_length) == 
                bytestream.fromvarlen(txout2.script_length)):
            print("  BAD tx_out.sript_length")
            print("   " + str(bytestream.fromvarlen(txout1.script_length)))
            print("   " + str(bytestream.fromvarlen(txout2.script_length)))
        else:
            print("  tx_out.script_length ok")
        if not (txout1.script.stream() == txout2.script.stream()):
            print("  BAD tx_out.script")
            print("   " + str(txout1.script.stream()))
            print("   " + str(txout2.script.stream()))
        else:
            print("  tx_out.script ok")
    if not (bytestream.fromunsigned(txn1.lock_time, 4) == 
            bytestream.fromunsigned(txn2.lock_time, 4)):
        print("BAD lock_time")
        print("   " + str(bytestream.fromunsigned(txn1.lock_time, 4)))
        print("   " + str(bytestream.fromunsigned(txn2.lock_time, 4)))
    else:
        print("lock_time ok")

    print("done show encoding")


def print_txin(txn1, txn2):
    for i,(x,y) in enumerate(zip(txn1.tx_in, txn2.tx_in)):
        print("\ntx in %s" % i)
        print("  prev hash: %s" % x.prev_hash)
        print("  prev hash: %s" % y.prev_hash)
        print("  index: %s " % x.index)
        print("  index: %s " % y.index)
        print("  script length: %s" % x.script_length)
        print("  script length: %s" % y.script_length)
        print("  script: %s" % x.script)
        print("  script: %s" % y.script)
        print("  sequence: %s" % x.sequence)
        print("  sequence: %s" % y.sequence)


if __name__ == '__main__':
    rpc_server = rpc.jsonrpc("bitcoinrpc", "Ck9SwPoZ76gaiLex88r7aKspUrFUFEDffai9mzRjDi7W")

    #conn_str = "dbname=postgres"
    conn_str = "dbname=abe2 user=yuewang"
    failures = Counts()
    errors = Counts()
    with psycopg2.connect(conn_str, cursor_factory=NamedTupleCursor) as conn:
        for i,hash in enumerate(some_hashes):
            print("\n verify hash %s" % i)
            abe_txn = Txn(hash, conn)
            rpc_txn = transaction.transaction(hash[2:], rpc_server)
            #print("\nencoding of abe transaction:")
            #show_encoding(t,txn)
            #print_txin(t, txn)
            try:
                print('abe verified: %s' % abe_txn.verify())
                failures.add('abe success')
            except Exception as e1:
                print(e1)
                errors.add(str(e1))
                failures.add('abe fail')
            finally:
                try:
                    print('rpc verified: %s' % rpc_txn.verify())
                    failures.add('rpc success')
                except Exception as e2:
                    print(e2)
                    errors.add(str(e2))
                    failures.add('rpc fail')
    failures.prn()
    errors.prn()
