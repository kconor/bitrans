import json
import urllib

class jsonrpc:
    def __init__(self, user, pwd, host="127.0.0.1", port="8332"):
        self.url = "http://%s:%s@%s:%s" % (user, pwd, host, port)
                
    def __call__(self, *args):
        method = args[0]
        params = args[1:]
        post = json.dumps({"jsonrpc": "2.0",
                           "method": method, "params": params, "id": "x"})
        response = urllib.urlopen(self.url, post).read()
        resp = json.loads(response)
        return resp['result']
        
    
    

    
