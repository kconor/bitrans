#!/usr/bin/env python2.7

import transaction
import rpc
import unittest
import os





class TestTx(unittest.TestCase):
    
    def test (self):
        # A transaction known to be successfully parsed by bitrans.     
        tx='fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4'


        result="""digraph g {
node0[shape=record,label="{(65)04f4...b3d3|(73)3046...4801}|{}"];
node1[shape=record,label="{(65)04f4...b3d3|(65)04f4...b3d3|(73)3046...4801}|{}"];
node0->node1[label="<118: OP_DUP>",color=blue,fontcolor=blue];
node2[shape=record,label="{(20)71d7...ad11|(65)04f4...b3d3|(73)3046...4801}|{}"];
node1->node2[label="<169: OP_HASH160>",color=blue,fontcolor=blue];
node3[shape=record,label="{(20)71d7...ad11|(20)71d7...ad11|(65)04f4...b3d3|(73)3046...4801}|{}"];
node2->node3[label="< 20: OP_PUSH20>",color=blue,fontcolor=blue];
node4[shape=record,label="{(65)04f4...b3d3|(73)3046...4801}|{}"];
node3->node4[label="<136: OP_EQUALVERIFY>",color=blue,fontcolor=blue];
node5[shape=record,label="{01}|{}"];
node4->node5[label="<172: OP_CHECKSIG>",color=blue,fontcolor=blue];
}"""

        
        # Read username and password from file that isn't checked into github
        try:
            fd=open("server.conf")
        except:
            print("Can't find a server.conf file. Expecting one with username and passwd on separate lines.")
        username,passwd =fd.read().split()
        s = rpc.jsonrpc(username,passwd)

        try:
            os.remove("graph.dot")
        except:
            pass
        
        t = transaction.transaction(tx,s) 
        test=False
#        t.verify(True)
#        test=open("graph.dot",'r').read()
        try:
            t.verify(True)
            test=open("graph.dot",'r').read()
        except:
            print ("\tException")
        print(test)
        
        self.assertEqual(test,result)


if __name__ == '__main__':
    print("Testing known transactions.\n")
    unittest.main()

