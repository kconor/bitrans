import ops
import bytestream
import script

def compile(filename):
    """
    Compile a .bt file into a script.

    """
    f = open(filename,'r')
    raw_string = f.read().replace('\n',' ')
    raw_list = [x for x in raw_string.split(' ') if x != '']
    parsed_list = []
    for item in raw_list:
        if len(item) > 1 and item[:2] == 'OP':
            try:
                parsed_list.append(ops.word[item])
            except KeyError:
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
    
