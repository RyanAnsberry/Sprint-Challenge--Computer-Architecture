"""CPU functionality."""

import sys

# op codes
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
HLT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        # memory
        self.ram = [0] * 256
        # registers
        self.reg = [0] * 8
        # program counter
        self.PC = 0
        # Stack pointer should be last register (7)
        self.SP = len(self.reg) - 1
        # assign SP register to end of memory
        self.reg[self.SP] = len(self.ram) - 1

        # flag register : 00000LGE
        self.FL = 0b00000000

        # Branchtable
        self.branchtable = {}
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[HLT] = self.hlt
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        self.branchtable[CMP] = self.compare
        self.branchtable[JMP] = self.jmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne

    # op functions
    # Save
    def ldi(self):
        operand_a = self.ram_read( self.PC + 1 )
        operand_b = self.ram_read( self.PC + 2 )
        self.reg[operand_a] = operand_b
        self.PC += 3

    # Print
    def prn(self):
        print_val = self.ram_read( self.PC + 1 )
        print( self.reg[print_val] ) 
        self.PC += 2

    # Multiply
    def mul(self):
        operand_a = self.ram_read( self.PC + 1 )
        operand_b = self.ram_read( self.PC + 2 )
        print(f"{self.reg[operand_a]} * {self.reg[operand_b]} =")
        self.reg[operand_a] *= self.reg[operand_b]
        self.PC += 3

    # Halt
    def hlt(self):
        self.running = False
        self.PC += 1

    # Push
    def push(self):
        register = self.ram[self.PC + 1]
        self.reg[self.SP] -= 1
        reg_value = self.reg[register]
        self.ram[self.reg[ self.SP] ] = reg_value
        self.PC += 2

    # Pop
    def pop(self):
        value = self.ram[ self.reg[self.SP] ]
        register = self.ram[self.PC + 1]
        self.reg[register] = value
        self.reg[self.SP] += 1
        self.PC += 2

    # Call
    def call(self):
        self.reg[self.SP] -= 1
        self.ram[ self.reg[self.SP] ] = self.PC + 2
        register = self.ram[self.PC + 1]
        self.PC = self.reg[register]

    # Return
    def ret(self):
        return_address = self.ram[ self.reg[self.SP] ]
        self.reg[self.SP] += 1
        self.PC = return_address

    # Add
    def add(self):
        reg1 = self.ram[self.PC + 1]
        reg2 = self.ram[self.PC + 2]
        self.alu("ADD", reg1, reg2)
        self.PC += 3

    # Compare
    def compare(self):
        reg1 = self.ram[self.PC + 1]
        reg2 = self.ram[self.PC + 2]
        self.alu("CMP", reg1, reg2)
        self.PC += 3

    # Jump
    def jmp(self):
        register = self.ram[self.PC + 1]
        self.PC = self.reg[register]

    # JEQ
    def jeq(self):
        register = self.ram[self.PC + 1]
        if self.FL & 0b00000001 == 1:
            self.PC = self.reg[register]
        else:
            self.PC += 2

    # JNE
    def jne(self):
        register = self.ram[self.PC + 1]
        if self.FL & 0b00000001 == 0:
            self.PC = self.reg[register]
        else:
            self.PC += 2

    # end op functions

    def load(self):
        """Load a program into memory."""
        address = 0
        # ensure two files passed in
        if len(sys.argv) != 2:
            print("Need proper file name passed in.")
            sys.exit(1)
        
        # access and assign second value (file to be loaded)
        filename = sys.argv[1]
        print(f"Filename: {filename}")
        with open(filename) as f:
            for line in f:
                # skip empty lines or comments
                if line == '\n' or line[0] == '#':
                    continue
                # separate comments from code
                comment_SPlit = line.split('#')
                # assign instruction num to variable and strip away extra SPaces
                instruction = comment_SPlit[0].strip()
                # cast instruction to int
                instruction_int = int(instruction, 2)
                # assign instruction num to address in ram and increment to next address
                self.ram[address] = instruction_int
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        while self.running:
            # Instruction Register
            IR = self.ram_read( self.PC )
            # check for valid operation
            if self.branchtable[IR]:
                self.branchtable[IR]()
            # Invalid command
            else:
                print(f"{IR} - command is not available")
                sys.exit(1)