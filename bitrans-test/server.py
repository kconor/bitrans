#add parent directory to path
import os
cwd = os.getcwd()
import sys
sys.path.append('/'.join(cwd.split('/')[:-1]))

import rpc


def connect():
    """
    Creates a connection to bitcoind.

    Credentials can be read from ~/.bitrans or from server.conf
    in the tests directory.
    """
    home = os.getenv("HOME")
    try:
        conf = open(home + "/.bitrans").read()
    except:
        try:
            conf=open("server.conf").read()
        except:
            raise Exception("Couldn't find/open a server credential file.  "\
                            "\nPlease create server.conf in the tests directory "\
                            "\nor .bitrans in your home directory with your "\
                            "\nbitcoind credentials separated by a newline.")
        
    username, passwd = conf.split()
    server = rpc.jsonrpc(username,passwd)
    return server
