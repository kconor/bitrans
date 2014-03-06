"""
An implementation of the bitcoin transaction script op codes, as
described in https://en.bitcoin.it/wiki/Script.

"""

import opfns
import bytestream

# Ops
class op:
    def __init__(self, word, opcode, f = lambda stream, machine: None):
        self.word = word
        self.opcode = opcode
        self.f = f

    def __call__(self, *args):
        self.f(*args)

    def __repr__(self):
        return "<%d: %s>" % (self.opcode, self.word)

    def __str__(self):
        return self.__repr__()

    def __cmp__(self, other):
        if self.opcode <  other.opcode:
            return -1
        elif self.opcode == other.opcode:
            return 0
        else:
            return 1

code = [None] * 256
code[0] = op("OP_0",
             0,
             opfns.empty_array)

# codes 1 through 75
for i in xrange(1,76):
    code[1] = op("",
                 i,
                 opfns.pusher_maker(i))

code[76] = op("OP_PUSHDATA1",
              76,
              opfns.reader_pusher_maker(1))
code[77] = op("OP_PUSHDATA2",
              77,
              opfns.reader_pusher_maker(2))
code[78] = op("OP_PUSHDATA4",
              77,
              opfns.reader_pusher_maker(4))
code[79] = op("OP_1NEGATE",
              79,
              opfns.numpusher_maker("FF"))
code[81] = op("OP_1",
              81,
              opfns.numpusher_maker("FF"))
code[82] = op("OP_2", 82)
code[83] = op("OP_3", 83)
code[84] = op("OP_4", 84)
code[85] = op("OP_5", 85)
code[86] = op("OP_6", 86)
code[87] = op("OP_7", 87)
code[88] = op("OP_8", 88)
code[89] = op("OP_9", 89)
code[90] = op("OP_10", 90)
code[91] = op("OP_11", 91)
code[92] = op("OP_12", 92)
code[93] = op("OP_13", 93)
code[94] = op("OP_14", 94)
code[95] = op("OP_15", 95)
code[96] = op("OP_16", 96)
code[97] = op("OP_NOP", 97)
code[99] = op("OP_IF", 99) #wrong args
code[100] = op("OP_NOTIF", 100) #wrong args
code[103] = op("OP_ELSE", 103) #wrong args
code[104] = op("OP_ENDIF", 104)
code[105] = op("OP_VERIFY", 105)
code[106] = op("OP_RETURN", 106)
code[107] = op("OP_TOALTSTACK", 107)
code[108] = op("OP_FROMALTSTACK", 108)
code[115] = op("OP_IFDUP", 115)
code[116] = op("OP_DEPTH", 116)
code[117] = op("OP_DROP", 117)
code[118] = op("OP_DUP", 118)
code[119] = op("OP_NIP", 119)
code[120] = op("OP_OVER", 120)
code[121] = op("OP_PICK", 121) 
code[122] = op("OP_ROLL", 122)
code[123] = op("OP_ROT", 123)
code[124] = op("OP_SWAP", 124)
code[125] = op("OP_TUCK", 125)
code[109] = op("OP_2DROP", 109)
code[110] = op("OP_2DUP", 110)
code[111] = op("OP_3DUP", 111)
code[112] = op("OP_2OVER", 112)
code[113] = op("OP_2ROT", 113)
code[114] = op("OP_2SWAP", 114)
code[130] = op("OP_SIZE", 130)
code[135] = op("OP_EQUAL", 135)
code[136] = op("OP_EQUALVERIFY", 136)
code[139] = op("OP_1ADD", 139)
code[140] = op("OP_1SUB", 140)
code[143] = op("OP_NEGATE", 143)
code[144] = op("OP_ABS", 144)
code[144] = op("OP_NOT", 145)
code[146] = op("OP_0NOTEQUAL", 146)
code[147] = op("OP_ADD", 147)
code[148] = op("OP_SUB", 148)
code[154] = op("OP_BOOLAND", 154)
code[155] = op("OP_BOOLOR", 155)
code[156] = op("OP_NUMEQUAL", 156)
code[157] = op("OP_NUMEQUALVERIFY", 157)
code[158] = op("OP_NUMNOTEQUAL", 158)
code[159] = op("OP_LESSTHAN", 159)
code[160] = op("OP_GREATHERTHAN", 160)
code[161] = op("OP_LESSTHANOREQUAL", 161)
code[162] = op("OP_GREATERTHANOREQUAL", 162)
code[163] = op("OP_MIN", 163)
code[164] = op("OP_MAX", 164)
code[165] = op("OP_WITHIN", 165)
code[166] = op("OP_RIPEMD160", 166) #wrong args
code[167] = op("OP_SHA1", 167)
code[168] = op("OP_SHA256", 168)
code[169] = op("OP_HASH160", 169)
code[170] = op("OP_HASH256", 170)
code[171] = op("OP_CODESEPARATOR", 171)
code[172] = op("OP_CHECKSIG", 172)
code[173] = op("OP_CHECKSIGVERIFY", 173)
code[174] = op("OP_CHECKMULTISIG", 174) #fix args
code[175] = op("OP_CHECKMULTISIGVERIFY", 175)w #fix args


