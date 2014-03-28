class machine:
    def __init__(self):
        self.stack = []
        self.alt = []

    def push(self, bstream):
        self.stack.append(bstream)

    def pushalt(self, bstream):
        self.alt.append(bstream)

    def pop(self, n=-1):
        return self.stack.pop(n)

    def popalt(self):
        return self.alt.pop()

    def peek(self, n=-1):
        return self.stack[n]

    def draw(self):
    	# If each item on the stack is 12 characters, just print it; otherwise num chars, first four, ldots, last four 
    	pretty_stack=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.stack[::-1]]
        print "\tstack |%10s [%s]" % ("*" * len(self.stack),', '.join(pretty_stack))
        pretty_alt=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.alt[::-1]]
        print "\talt   |%10s %s" % ("*" * len(self.alt),', '.join(pretty_alt))  


    	    
        
