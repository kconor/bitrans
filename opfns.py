# op function implementations
def empty_array(stream, machine):
    empty_array = bytestream("")
    stream.push(empty_array)
    return empty_array

def pusher_maker(i):
    def pusher(stream, machine):
        data = stream.read(i)
        machine.push(data)
        return data
    return pusher

def reader_pusher_maker(i):
    def reader_pusher(stream, machine):
        nbytes = stream.read(i).unsigned()
        data = stream.read(nbytes)
        machine.push(i)
        return data
    return reader_pusher

def numpusher_maker(string):
    def numpusher(stream, machine):
        data = bytestream(string)
        machine.push(data)
        return data
    return numpusher
        
