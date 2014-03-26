import ops
import bytestream
import script

def compile(filename):
    """
    Extremely quick hack of a compiler.  If something looks like it doesn't make sense, it probobably doesn't make sense.

    """
    f = open(filename,'r')
    raw_string = f.read().replace('\n',' ')
    raw_list = [x for x in raw_string.split(' ') if x != '']
    parsed_list = []
    for item in raw_list:
        if len(item) > 1 and item[:2] == 'OP':
            # slow, should index ops by word too
            found = False
            for op in ops.code:
                if op is not None and op.word == item:
                    parsed_list.append(op)
                    found = True
                    break
            if not found:
                print "Unrecognized op %s" % (item,)
                return
        else:
            parsed_list.append(bytestream.bytestream(item))
    stream = bytestream.bytestream('')
    for parsed_item in parsed_list:
        if(isinstance(parsed_item, ops.op)):
            stream += parsed_item.stream()
        else:
            stream += parsed_item
    return script.script(stream)
    
