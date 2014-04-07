#add parent directory to path
import os
cwd = os.getcwd()
import sys
sys.path.append('/'.join(cwd.split('/')[:-1]))

import server
import transaction 
from nose.tools import assert_true



hashes=[
        # currently passing in bitrans:
        'fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4',
        'fbde5d03b027d2b9ba4cf5d4fecab9a99864df2637b25ea4cbcb1796ff6550ca',
        'a4bfa8ab6435ae5f25dae9d89e4eb67dfa94283ca751f393c1ddc5a837bbc31b',
        # currently failing in bitrans:
        '220ebc64e21abece964927322cba69180ed853bb187fbc6923bac7d010b9d87a',
]     

def transaction_test():
    conn = server.connect()
    for tx_hash in hashes: #each hash is its own test case
        yield assert_true, transaction.transaction(tx_hash, conn).verify()
