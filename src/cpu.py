from cartridge import nesCart
from itertools import count

exTypeDecode = lambda opcode : (opcode & 0x3)
adModeDecode = lambda opcode : (opcode & 0x1C) >> 2
opDecode = lambda opcode : (opcode & 0xE0) >> 5
hiDecode = lambda opcode : (opcode & 0xE0)
loDecode = lambda opcode : (opcode & 0x1F)
## will need to make 3 tables of the applicable opcodes
## and addressing modes, since not all are available
## although, valid programs shouldnt use the invalid ops

otherOps = {
    0x78 : (1, 1)
}

addressingMode0 = {
    0 : ('#immediate', 2, 2),
    1 : ('zero page', 3, 2),
    2 : ('NOP', 1, 1),
    3 : ('absolute',4, 3),
    4 : ('NOP', 1, 1),
    5 : ('zero page,X',1, 1),
    6 : ('NOP',1, 1),
    7 : ('absolute,X', 1, 1),
}

addressingMode1 = {
#  op : (addrModeName, cycles, additional instr)
    0 : ('(indirect,X)',6, 2),
    1 : ('zero page',3, 2),
    2 : ('#immediate',2, 2),
    3 : ('absolute',4, 3),
    4 : ('(indirect),Y',5, 2), # +1 Cycle if Page crossed
    5 : ('zero page,X',4, 2),
    6 : ('absolute,Y',4, 3), # +1 Cycle if Page crossed
    7 : ('absolute,X',4, 3), # +1 Cycle if Page crossed
}

addressingMode2 = {
#  op : (addrModeName, cycles, additional instr)
    0 : ('#immediate', 1, 1),
    1 : ('zero page', 1, 1),
    2 : ('accumulator', 1, 1),
    3 : ('absolute', 1, 1),
    4 : ('NOP', 1, 1),
    5 : ('zero page,X', 1, 1),
    6 : ('NOP', 1, 1),
    7 : ('absolute,X', 1, 1),
}

opMode0 = {
    0 : 'NOP',
    1 : 'BIT',
    2 : 'JMP',
    3 : 'JMP(ABS)',
    4 : 'STY',
    5 : 'LDY',
    6 : 'CPY',
    7 : 'CPX',
}

opMode1 = {
    0 : 'ORA',
    1 : 'AND',
    2 : 'EOR',
    3 : 'ADC',
    4 : 'STA',
    5 : 'LDA',
    6 : 'CMP',
    7 : 'SBC',
}

opMode2 = {
#  op : (addrModeName, cycles, additional instr)
    0 : 'ASL',
    1 : 'ROL',
    2 : 'LSR',
    3 : 'ROR',
    4 : 'STX',
    5 : 'LDX',
    6 : 'DEC',
    7 : 'INC',
}

instructionMode = {
    0 : (addressingMode0, opMode0),
    1 : (addressingMode1, opMode1),
    2 : (addressingMode2, opMode2),
    3 : None
}

controlAddressingModes = {
    0 : '#immediate',
    1 : 'zero page',
    2 : 'implied',
    3 : 'absolute',
    4 : 'NOP',
    5 : 'zero page,X',
    6 : 'implied',
    7 : 'absolute,X',
    8 : '(absolute)'
}

# ('OP', ADDRMODE, BASE_CYCLES, BYTES)
controlOps = {
    0x00 : {
        0x00 : ('BRK', 2, 7, 1), 0x04 : ('NOP', 1, 3, 2), 0x08 : ('PHP', 2, 3, 1), 0x0C : ('NOP', 3, 4, 3),
        0x10 : ('BPL', 4, 2, 2), 0x14 : ('NOP', 5, 1, 1), 0x18 : ('CLC', 6, 2, 1), 0x1C : ('NOP', 7, 1, 1),
    },
    0x20 : {
        0x00 : ('JSR', 3, 6, 3), 0x04 : ('BIT', 1, 3, 2), 0x08 : ('PLP', 2, 4, 1), 0x0C : ('BIT', 3, 4, 3),
        0x10 : ('BMI', 4, 2, 2), 0x14 : ('NOP', 5, 1, 1), 0x18 : ('SEC', 6, 2, 1), 0x1C : ('NOP', 7, 1, 1),
    },
    0x40 : {
        0x00 : ('RTI', 2, 6, 1), 0x04 : ('NOP', 1, 3, 2), 0x08 : ('PHA', 2, 3, 1), 0x0C : ('JMP', 3, 3, 3),
        0x10 : ('BVC', 4, 2, 2), 0x14 : ('NOP', 5, 1, 1), 0x18 : ('CLI', 6, 2, 1), 0x1C : ('NOP', 7, 1, 1),
    },
    0x60 : {
        0x00 : ('RTS', 2, 6, 1), 0x04 : ('NOP', 1, 3, 2), 0x08 : ('PLA', 2, 4, 1), 0x0C : ('JMP', 8, 5, 3),
        0x10 : ('BVS', 4, 2, 2), 0x14 : ('NOP', 5, 1, 1), 0x18 : ('SEI', 6, 2, 1), 0x1C : ('NOP', 7, 1, 1),
    },
    0x80 : {
        0x00 : ('NOP', 0, 2, 2), 0x04 : ('STY', 1, 3, 2), 0x08 : ('DEY', 2, 2, 1), 0x0C : ('STY', 3, 4, 3),
        0x10 : ('BCC', 4, 2, 2), 0x14 : ('STY', 5, 4, 2), 0x18 : ('TYA', 6, 2, 1), 0x1C : ('SHY', 7, 1, 1),
    },
    0xA0 : {
        0x00 : ('LDY', 0, 2, 2), 0x04 : ('LDY', 1, 3, 2), 0x08 : ('TAY', 2, 2, 1), 0x0C : ('LDY', 3, 4, 3),
        0x10 : ('BCS', 4, 2, 2), 0x14 : ('LDY', 5, 4, 2), 0x18 : ('CLV', 6, 2, 1), 0x1C : ('LDY', 7, 4, 3),
    },
    0xC0 : {
        0x00 : ('CPY', 0, 2, 2), 0x04 : ('CPY', 1, 3, 2), 0x08 : ('INY', 2, 2, 1), 0x0C : ('CPY', 3, 4, 3),
        0x10 : ('BNE', 4, 2, 2), 0x14 : ('NOP', 5, 1, 1), 0x18 : ('CLD', 6, 2, 1), 0x1C : ('NOP', 7, 1, 1),
    },
    0xE0 : {
        0x00 : ('CPX', 0, 2, 2), 0x04 : ('CPX', 1, 3, 2), 0x08 : ('INX', 2, 2, 1), 0x0C : ('CPX', 3, 4, 3),
        0x10 : ('BEQ', 4, 2, 2), 0x14 : ('NOP', 5, 1, 1), 0x18 : ('SED', 6, 2, 1), 0x1C : ('NOP', 7, 1, 1),
    },
}

aluAddressingMode = {
#  op : (addrModeName, cycles, additional instr)
    0 : '(indirect,X)',
    1 : 'zero page',
    2 : '#immediate',
    3 : 'absolute',
    4 : '(indirect),Y', # +1 Cycle if Page crossed
    5 : 'zero page,X',
    6 : 'absolute,Y', # +1 Cycle if Page crossed
    7 : 'absolute,X', # +1 Cycle if Page crossed
}

aluOps = {
    0x00 : {
        0x01 : ('ORA', 0, 6, 2), 0x05 : ('ORA', 1, 3, 2), 0x09 : ('ORA', 2, 2, 2), 0x0D : ('ORA', 3, 4, 3),
        0x11 : ('ORA', 4, 5, 2), 0x15 : ('ORA', 5, 4, 2), 0x19 : ('ORA', 6, 4, 3), 0x1D : ('ORA', 7, 4, 3),
    },
    0x20 : {
        0x01 : ('AND', 0, 6, 2), 0x05 : ('AND', 1, 3, 2), 0x09 : ('AND', 2, 2, 2), 0x0D : ('AND', 3, 4, 3),
        0x11 : ('AND', 4, 5, 2), 0x15 : ('AND', 5, 4, 2), 0x19 : ('AND', 6, 4, 3), 0x1D : ('AND', 7, 4, 3),
    },
    0x40 : {
        0x01 : ('EOR', 0, 6, 2), 0x05 : ('EOR', 1, 3, 2), 0x09 : ('EOR', 2, 2, 2), 0x0D : ('EOR', 3, 4, 3),
        0x11 : ('EOR', 4, 5, 2), 0x15 : ('EOR', 5, 4, 2), 0x19 : ('EOR', 6, 4, 3), 0x1D : ('EOR', 7, 4, 3),
    },
    0x60 : {
        0x01 : ('ADC', 0, 6, 2), 0x05 : ('EOR', 1, 3, 2), 0x09 : ('EOR', 2, 2, 2), 0x0D : ('EOR', 3, 4, 3),
        0x11 : ('EOR', 4, 5, 2), 0x15 : ('EOR', 5, 4, 2), 0x19 : ('EOR', 6, 4, 3), 0x1D : ('EOR', 7, 4, 3),
    },
    0x80 : {
        0x01 : ('STA', 0, 6, 2), 0x05 : ('STA', 1, 3, 2), 0x09 : ('NOP', 2, 1, 2), 0x0D : ('STA', 3, 4, 3),
        0x11 : ('STA', 4, 5, 2), 0x15 : ('STA', 5, 4, 2), 0x19 : ('STA', 6, 4, 3), 0x1D : ('STA', 7, 4, 3),
    },
    0xA0 : {
        0x01 : ('LDA', 0, 6, 2), 0x05 : ('LDA', 1, 3, 2), 0x09 : ('LDA', 2, 2, 2), 0x0D : ('LDA', 3, 4, 3),
        0x11 : ('LDA', 4, 5, 2), 0x15 : ('LDA', 5, 4, 2), 0x19 : ('LDA', 6, 4, 3), 0x1D : ('LDA', 7, 4, 3),
    },
    0xC0 : {
        0x01 : ('CMP', 0, 6, 2), 0x05 : ('CMP', 1, 3, 2), 0x09 : ('CMP', 2, 2, 2), 0x0D : ('CMP', 3, 4, 3),
        0x11 : ('CMP', 4, 5, 2), 0x15 : ('CMP', 5, 4, 2), 0x19 : ('CMP', 6, 4, 3), 0x1D : ('CMP', 7, 4, 3),
    },
    0xE0 : {
        0x01 : ('SBC', 0, 6, 2), 0x05 : ('SBC', 1, 3, 2), 0x09 : ('SBC', 2, 2, 2), 0x0D : ('SBC', 3, 4, 3),
        0x11 : ('SBC', 4, 5, 2), 0x15 : ('SBC', 5, 4, 2), 0x19 : ('SBC', 6, 4, 3), 0x1D : ('SBC', 7, 4, 3),
    },
}

rmwAddressingModes = {
#  op : (addrModeName, cycles, additional instr)
    0 : '#immediate',
    1 : 'zero page',
    2 : 'implied',
    3 : 'absolute',
    4 : 'implied',
    5 : 'zero page,X',
    6 : 'zero page,Y',
    7 : 'implied',
    8 : 'absolute,X',
    9 : 'absolute,Y',
}

rmwOps = {
    0x00 : {
        0x02 : ('STP', 2, 1, 1), 0x06 : ('ASL', 1, 5, 2), 0x0A : ('ASL', 2, 2, 1), 0x0E : ('ASL', 3, 6, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('ASL', 5, 6, 2), 0x1A : ('NOP', 7, 1, 1), 0x1E : ('ASL', 8, 7, 3),
    },
    0x20 : {
        0x02 : ('STP', 2, 1, 1), 0x06 : ('ROL', 1, 5, 2), 0x0A : ('ROL', 2, 2, 1), 0x0E : ('ROL', 3, 6, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('ROL', 5, 6, 2), 0x1A : ('NOP', 7, 1, 1), 0x1E : ('ROL', 8, 7, 3),
    },
    0x40 : {
        0x02 : ('STP', 2, 1, 1), 0x06 : ('LSR', 1, 5, 2), 0x0A : ('LSR', 2, 2, 1), 0x0E : ('LSR', 3, 6, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('LSR', 5, 6, 2), 0x1A : ('NOP', 7, 1, 1), 0x1E : ('LSR', 8, 7, 3),
    },
    0x60 : {
        0x02 : ('STP', 2, 1, 1), 0x06 : ('ROR', 1, 5, 2), 0x0A : ('ROR', 2, 2, 1), 0x0E : ('ROR', 3, 6, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('ROR', 5, 6, 2), 0x1A : ('NOP', 7, 1, 1), 0x1E : ('ROR', 8, 7, 3),
    },
    0x80 : {
        0x02 : ('NOP', 0, 1, 1), 0x06 : ('STX', 1, 3, 2), 0x0A : ('TXA', 2, 2, 1), 0x0E : ('STX', 3, 4, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('STX', 6, 4, 2), 0x1A : ('TXS', 7, 2, 1), 0x1E : ('SHX', 9, 1, 1),
    },
    0xA0 : {
        0x02 : ('LDX', 0, 2, 2), 0x06 : ('LDX', 1, 3, 2), 0x0A : ('TAX', 2, 2, 1), 0x0E : ('LDX', 3, 4, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('LDX', 6, 4, 2), 0x1A : ('TSX', 7, 2, 1), 0x1E : ('LDX', 9, 4, 3),
    },
    0xC0 : {
        0x02 : ('NOP', 0, 1, 1), 0x06 : ('DEC', 1, 5, 2), 0x0A : ('DEX', 2, 2, 1), 0x0E : ('DEC', 3, 6, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('DEC', 5, 6, 2), 0x1A : ('NOP', 7, 1, 1), 0x1E : ('DEC', 8, 7, 3),
    },
    0xE0 : {
        0x02 : ('NOP', 0, 1, 1), 0x06 : ('INC', 1, 5, 2), 0x0A : ('NOP', 2, 1, 1), 0x0E : ('INC', 3, 6, 3),
        0x12 : ('STP', 4, 1, 1), 0x16 : ('INC', 5, 6, 2), 0x1A : ('NOP', 7, 1, 1), 0x1E : ('INC', 8, 7, 3),
    },
}

datMvAddressingModes = {
#  op : (addrModeName, cycles, additional instr)
    0 : '(indirect,X)',
    1 : 'zero page',
    2 : '#immediate',
    3 : 'absolute',
    4 : '(indirect),Y', # +1 Cycle if Page crossed
    5 : 'zero page,X',
    6 : 'absolute,Y', # +1 Cycle if Page crossed
    7 : 'absolute,X', # +1 Cycle if Page crossed
}

dataMvOps = {
    0x00 : {
        0x03 : ('SLO', 0, 1, 1), 0x07 : ('SLO', 1, 1, 1), 0x0B : ('ANC', 2, 1, 1), 0x0F : ('SLO', 3, 1, 1),
        0x13 : ('SLO', 4, 1, 1), 0x17 : ('SLO', 5, 1, 1), 0x1B : ('SLO', 6, 1, 1), 0x1F : ('SLO', 7, 1, 1),
    },
    0x20 : {
        0x03 : ('RLA', 0, 1, 1), 0x07 : ('RLA', 1, 1, 1), 0x0B : ('ANC', 2, 1, 1), 0x0F : ('RLA', 3, 1, 1),
        0x13 : ('RLA', 4, 1, 1), 0x17 : ('RLA', 5, 1, 1), 0x1B : ('RLA', 6, 1, 1), 0x1F : ('RLA', 7, 1, 1),
    },
    0x40 : {
        0x03 : ('SRE', 0, 1, 1), 0x07 : ('SRE', 1, 1, 1), 0x0B : ('ALR', 2, 1, 1), 0x0F : ('SRE', 3, 1, 1),
        0x13 : ('SRE', 4, 1, 1), 0x17 : ('SRE', 5, 1, 1), 0x1B : ('SRE', 6, 1, 1), 0x1F : ('SRE', 7, 1, 1),
    },
    0x60 : {
        0x03 : ('RRA', 0, 1, 1), 0x07 : ('RRA', 1, 1, 1), 0x0B : ('ARR', 2, 1, 1), 0x0F : ('RRA', 3, 1, 1),
        0x13 : ('RRA', 4, 1, 1), 0x17 : ('RRA', 5, 1, 1), 0x1B : ('RRA', 6, 1, 1), 0x1F : ('RRA', 7, 1, 1),
    },
    0x80 : {
        0x03 : ('SAX', 0, 1, 1), 0x07 : ('SAX', 1, 1, 1), 0x0B : ('XAA', 2, 1, 1), 0x0F : ('SAX', 3, 1, 1),
        0x13 : ('AHX', 4, 1, 1), 0x17 : ('SAX', 5, 1, 1), 0x1B : ('TAS', 6, 1, 1), 0x1F : ('AHX', 6, 1, 1),
    },
    0xA0 : {
        0x03 : ('LAX', 0, 1, 1), 0x07 : ('LAX', 1, 1, 1), 0x0B : ('LAX', 2, 1, 1), 0x0F : ('LAX', 3, 1, 1),
        0x13 : ('LAX', 4, 1, 1), 0x17 : ('LAX', 5, 1, 1), 0x1B : ('LAS', 6, 1, 1), 0x1F : ('LAX', 6, 1, 1),
    },
    0xC0 : {
        0x03 : ('DCP', 0, 1, 1), 0x07 : ('DCP', 1, 1, 1), 0x0B : ('AXS', 2, 1, 1), 0x0F : ('DCP', 3, 1, 1),
        0x13 : ('DCP', 4, 1, 1), 0x17 : ('DCP', 5, 1, 1), 0x1B : ('DCP', 6, 1, 1), 0x1F : ('DCP', 7, 1, 1),
    },
    0xE0 : {
        0x03 : ('ISC', 0, 1, 1), 0x07 : ('ISC', 1, 1, 1), 0x0B : ('SBC', 2, 1, 1), 0x0F : ('ISC', 3, 1, 1),
        0x13 : ('ISC', 4, 1, 1), 0x17 : ('ISC', 5, 1, 1), 0x1B : ('ISC', 6, 1, 1), 0x1F : ('ISC', 7, 1, 1),
    },
}

opModes = {
    0 : controlOps,
    1 : aluOps,
    2 : rmwOps,
    3 : dataMvOps,
}

addrInfo = {
    0 : controlAddressingModes,
    1 : aluAddressingMode,
    2 : rmwAddressingModes,
    3 : datMvAddressingModes,
}


class CPU:
    pc = 0
    sp = 0
    A = 0
    x = 0
    y = 0
    status = 0
    def __init__(self):
        ## for debugging only
        self.cart = nesCart("../nes/Super Mario Bros. (Japan, USA).nes")
        pass

    def __str__(self) -> str:
        ret = f"""CPU STATUS
        PC: {self.pc}
        SP: {self.sp}
        A: {self.A}
        X: {self.x}
        Y: {self.y}
        Status: {self.status}
        """

        return ret
    
    @staticmethod
    def printOpInfo(opcode):
        instInfo = instructionMode[exTypeDecode(opcode)]
        op = instInfo[1][opDecode(opcode)]
        adInfo = instInfo[0][adModeDecode(opcode)]
        print(f"{op} {adInfo[0]}, Cycles: {adInfo[1]}, Bytes {adInfo[2]}")

    @staticmethod
    def printOpCode(opcode):
        exMode = exTypeDecode(opcode)
        opInfo = opModes[exMode][hiDecode(opcode)][loDecode(opcode)]

        print(f"{opInfo[0]} {addrInfo[exMode][opInfo[1]]}")
        

    def clock(self):
        op = self.cart.PRGM[0][self.pc]   # using page 0 here.  mapper would ideally swap this out
        opInfo = opModes[exTypeDecode(op)][hiDecode(op)][loDecode(op)]
        if opInfo[0] == 'ADC':
            self.printOpCode(op)
            # get opcode class
            exOp = globals()[opInfo[0]]
            ex = exOp(self, *opInfo)
            ex.execute(self)
        self.pc += opInfo[3]
        
## Instruction class, Addressing class 
## instruction class tells the operation, addressing class tells how its stored and how many cycles

'''
# Addressing modes
Accumulator - modify A directly


# ALU
accumulator - A := A op {adr}
(indirect,X)
zero page   -- operate on value in 8 bit address
#immediate  -- operate directly on value given
absolute    -- operate on value in 16 bit address
(indirect),Y -- operate on value 
zero page,X
absolute,Y 
absolute,X 

()

'''
class ADDR:
    def __init__(self, cpu, instData):
        self.instData = instData
        self._info = ''
        pass

    def getValue(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.info

class IMMEDIATE(ADDR):
    '''
    symbol -> #v

    LDA #10 ;Load 10 ($0A) into the accumulator

    str: #{arg}
    '''
    def __init__(self, cpu, instData):
        super().__init__(cpu, instData)
        self._info = '#immediate'
        self.val = instData[0]
        
    def getValue(self):
        # returns the value to use in the operation and additional
        # cycle counts
        return self.value, 0   

    def __str__(self):
        return f'#{self.val}'

class ZEROPAGE(ADDR):
    '''
    symbol -> d

    LDA $00         ;Load accumulator from $00

    str: ${arg}
    '''
    def __init__(self, cpu, instData) -> None:
        super().__init__(cpu, instData)

    def execute(self, cpu) -> int:

        return 2

class ACCUMULATOR(ADDR):
    '''
    symbol -> A

    LSR A           ;Logical shift right one bit

    str: A
    '''
    def __init__(self) -> None:
        pass

class ZEROPAGEX(ADDR):
    '''
    symbol -> d,x

    formula -> val = PEEK((arg + X) % 256)

    cycles -> 4

    STY $10,X       ;Save the Y register at location on zero page

    str: ${arg}, X
    '''
    def __init__(self) -> None:
        pass

class ZEROPAGEY(ADDR):
    '''
    symbol -> d,y

    formula -> val = PEEK((arg + Y) % 256)

    cycles -> 4

    LDX $10,Y       ;Load the X register from a location on zero page

    str: ${arg}, Y
    '''
    def __init__(self) -> None:
        pass

class RELATIVE(ADDR):
    '''
    symbol -> label

    used by branch instructions

    BEQ LABEL       ;Branch if zero flag set to LABEL
    BNE *+4         ;Skip over the following 2 byte instruction
    
    str: ${arg}
    '''
    def __init__(self) -> None:
        pass

class ABSOLUTE(ADDR):
    '''
    symbol -> a

    JMP $1234       ;Jump to location $1234
    needs join of 2 8bit values

    str: ${arg}
    '''
    def __init__(self) -> None:
        pass

class ABSOLUTEX(ADDR):
    '''
    symbol -> a,x

    formula -> val = PEEK(arg + X)

    cycles -> 4+ add 1 cycle if page boundary is crossed ie 256 value wraps

    needs join of 2 8bit values
    STA $3000,X     ;Store accumulator between $3000 and $30FF

    str: ${arg}, X
    '''
    def __init__(self) -> None:
        pass

class ABSOLUTEY(ADDR):
    '''
    symbol -> a,y

    formula -> val = PEEK(arg + Y)

    cycles -> 4+ add 1 cycle if page boundary is crossed ie 256 value wraps

    needs join of 2 8bit values
    AND $4000,Y     ;Perform a logical AND with a byte of memory

    str: ${arg}, Y
    '''
    def __init__(self) -> None:
        pass

class INDIRECT(ADDR):
    '''
    symbol -> (a)

    JMP ($FFFC)     ;Force a power on reset

    str: (${arg})
    '''
    def __init__(self) -> None:
        pass

class IDXINDIRECT(ADDR):
    '''
    symbol -> (d,x)

    formula -> val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)

    cycles -> 6

    LDA ($40,X)     ;Load a byte indirectly from memory

    str: (${arg}, X)
    '''
    def __init__(self) -> None:
        pass

class INDIRECTIDX(ADDR):
    '''
    symbol -> (d),y

    formula -> val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)

    cycles -> 5+ add 1 cycle if page boundary is crossed ie 256 value wraps

    LDA ($40),Y     ;Load a byte indirectly from memory

    str: (${arg}), Y
    '''
    def __init__(self) -> None:
        pass

addrModes = {

    'IMMEDIATE' : IMMEDIATE,
}


class OP:
    def __init__(self, cpu, op, addrMode, cycles, byteCount):
        self.op = op
        self.addrMode = addrMode
        self.cycles = cycles
        self.byteCount = byteCount
        self.instData = []
        self.rep = 'Base Class OP'

        for i in range(byteCount):
            self.instData.append(cpu.cart.PRGM[0][cpu.pc + i])
        
    
    def execute(self, cpu):
        raise NotImplementedError

    def __str__(self) -> str:
        return self.rep


class ADC(OP):
    def __init__(self, cpu, op, addrMode, cycles, byteCount):
        super().__init__(cpu, op, addrMode, cycles, byteCount)
        #create string        
        self.addrMode = addrModes['IMMEDIATE'](cpu, self.instData)
        #self.rep = f"{op} {self.instData[1:]}"
        self.rep = f"{op} {self.addrMode}"

    def execute(self, cpu):
        self.addrMode.getValue()
        print(self)
        

class ORA(OP):
    def __init__(self, cpu, op, addrMode, cycles, byteCount):
        super().__init__(cpu, op, addrMode, cycles, byteCount)
        self.rep = f"{op} {self.instData[1:]}"
    
    def execute(self, cpu):
        print(self)
        

def main():
    cpu = CPU()
    for _ in range(len(cpu.cart.PRGM[0])):
        cpu.clock()

        


if __name__ == "__main__":
    main()


