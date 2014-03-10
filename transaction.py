import bytestream

class transaction:
    def __init__(self, string):
        stream = bytestream.bytestream(string)
        self.version = stream.read(4).unsigned()
        
