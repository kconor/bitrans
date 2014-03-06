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
        
        
        
