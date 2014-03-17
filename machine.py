class machine:
    def __init__(self):
        self.stack = []
        self.alt = []

    def push(self, bstream):
        self.stack.append(bstream)

    def pushalt(self, bstream):
        self.alt.append(bstream)

    def pop(self):
        return self.stack.pop()

    def popalt(self):
        return self.alt.pop()

    def peek(self, n = -1):
        return self.stack[n]

    def draw(self):
        print "stack |%s" % ("*" * len(self.stack),)
        print "alt   |%s" % ("*" * len(self.alt),)
        
        
        
