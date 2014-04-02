#!/usr/bin/env python2.7

import transaction
import rpc
import unittest

class TestTx(unittest.TestCase):
    
    def test (self):
        # A list of transactions posted to the block chain that are known to be successfully parsed by bitrans.     
        passes=[
            'fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4',
            'fbde5d03b027d2b9ba4cf5d4fecab9a99864df2637b25ea4cbcb1796ff6550ca'
            ]
        # A list of transactions posted to the block chain that are known NOT to be successfully parsed by bitrans. 
        # These transactions either return false (shouldn't happen if posted to block chain) or raise an exception.          
        fails=[
            '220ebc64e21abece964927322cba69180ed853bb187fbc6923bac7d010b9d87a',
            'a4bfa8ab6435ae5f25dae9d89e4eb67dfa94283ca751f393c1ddc5a837bbc31b'
            ]     
        
        # Read username and password from file that isn't checked into github
        try:
            fd=open("server.conf")
        except:
            print("Can't find a server.conf file. Expecting one with username and passwd on separate lines.")
        username,passwd =fd.read().split()
        s = rpc.jsonrpc(username,passwd)


        for (test_set,result) in [(passes,True),(fails,False)]: 
            for tx in test_set:
                print(tx)
                print ("\nExpecting a result of %s." % result)
                t = transaction.transaction(tx,s) 
                try:
                    test= t.verify(True)
                except:
                    print ("\tException")
                    test= False
                print("Found a result of %s." % test)
                self.assertEqual(test,result)


if __name__ == '__main__':
    print("Testing known transactions.\n")
    unittest.main()

