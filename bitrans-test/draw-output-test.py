#add parent directory to path
import os
cwd = os.getcwd()
import sys
sys.path.append('/'.join(cwd.split('/')[:-1]))

import server
import transaction
import unittest
from nose.tools import assert_equal



# A transaction known to be successfully parsed by bitrans.     
tx_hash='fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4'


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

        
def test():
    conn = server.connect()
    try:
        os.remove("graph.dot")
    except:
        pass
    txn = transaction.transaction(tx_hash,conn) 
    test=False

    txn.verify(True)
    test=open("graph.dot",'r').read()

    print(test)
    
    assert_equal(test,result)
