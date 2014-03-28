class machine:
    def __init__(self):
        self.stack = []
        self.alt = []
        # dot requires each node have a unique number
        self.draw_cnt=0
        # open a file for writing a graphviz/dot file; write the header
        # todo: write each transaction to a different dot file?
        self.fd = open("graph.dot","w")
        self.fd.write("digraph g {\n")
		
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

    def draw(self,op=None):
		""" Writes to stdout a text-version of the stack and ops; also calls method to write dot """
		
    	# If each item on the stack is 12 characters, just print it; otherwise num chars, first four, ldots, last four 
    	pretty_stack=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.stack[::-1]]
        print("\tstack |%10s [%s]" % ("*" * len(self.stack),', '.join(pretty_stack)))
        pretty_alt=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.alt[::-1]]
        print("\talt   |%10s %s" % ("*" * len(self.alt),', '.join(pretty_alt)))
        self.dot(op)
        
    def dot(self,op):
    	""" Writes a graphviz/dot language string for the next operation and the current stack and alt stack """
    	
       	# If each item on the stack is 12 characters, just print it; otherwise num chars, first four, ldots, last four 
    	pretty_stack=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.stack[::-1]]
        pretty_alt=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.alt[::-1]]
        
    	# { } means stack vertically. | separates the items within the record
    	label = "\"{%s}|{%s}\"" % ('|'.join(pretty_stack),'|'.join(pretty_alt))
        self.fd.write("node%d[shape=record,label=%s];\n" %(self.draw_cnt,label))
        # draw an edge from the previous node
    	if (self.draw_cnt>0):
    		self.fd.write("node%d->node%d[label=\"%s\",color=blue,fontcolor=blue];\n" %(self.draw_cnt-1,self.draw_cnt,str(op)))
    	self.draw_cnt+=1

    def draw_close(self):
    	""" graphviz/dot files aren't valid without a closing brace """
    	
        self.fd.write("}")
        self.fd.close