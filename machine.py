str2ifstate = {"eval-consequent": 0,
               "ignore-consequent": 1,
               "eval-alternative": 2,
               "ignore-alternative": 3}
ifstate2str = ["eval-consequent", "ignore-consequent", "eval-alternative", "ignore-alternative"]

class machine:
    def __init__(self):
        # init stacks
        self.stack = []
        self.alt = []

        # init state
        self.ifstate = []
        self.locked = False  # if locked, mutation is forbidden
        
        # dot requires each node have a unique number
        self.draw_cnt=0
        # open a file for writing a graphviz/dot file; write the header
        # todo: write each transaction to a different dot file?
        self.fd = open("graph.dot","w")
        self.fd.write("digraph g {\n")
        
    def __del__(self):
        """ graphviz/dot files aren't valid without a closing brace """
        
        self.fd.write("}")
        self.fd.close

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False
        
    def push(self, bstream):
        if not self.locked:
            self.stack.append(bstream)

    def pushalt(self, bstream):
        if not self.locked:
            self.alt.append(bstream)

    def pushifstate(self, string):
        if not self.locked:
            self.ifstate.append(str2ifstate[string])

    def changeifstate(self, string):
        if not self.locked:
            self.ifstate[-1] = str2ifstate[string]

    def pop(self, n=-1):
        if not self.locked:
            return self.stack.pop(n)

    def popalt(self):
        if not self.locked:
            return self.alt.pop()

    def popifstate(self):
        if not self.locked:
            return ifstate2str[self.ifstate.pop()]
        
    def peek(self, n=-1):
        return self.stack[n]

    def inif(self):
        """
        Are we currently within an if-else block?

        """
        return len(self.ifstate) != 0

    def inifstate(self, string):
        return ifstate2str[self.ifstate[-1]] == string

    def draw(self,op=None):
        """ 
            Writes to stdout a text-version of the stack and ops; also calls method to write dot.
            Also writes a graphviz/dot language string for the next operation and the current stack 
            and alt stack 
        """
        
        # If each item on the stack is 12 characters, just print it; otherwise num chars, first four, ldots, last four 
        pretty_stack=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.stack[::-1]]
        print("\tstack |%10s [%s]" % ("*" * len(self.stack),', '.join(pretty_stack)))
        pretty_alt=  [str(x) if len(x)<12 else "(%s)%s...%s"%(len(x),str(x)[:4],str(x)[-4:]) for x in self.alt[::-1]]
        print("\talt   |%10s %s" % ("*" * len(self.alt),', '.join(pretty_alt)))
        
        # Write the dot file
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


