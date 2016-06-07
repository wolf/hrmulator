import re

from CPUInstructions import *


class Assembler:
    InstructionCatalog = [
        NoOp,
        MoveFromInbox,
        MoveToOutbox,
        CopyTo,
        CopyFrom,
        Add,
        Subtract,
        Jump,
        JumpIfZero,
        JumpIfNegative,
        BumpUp,
        BumpDown
    ]

    def __init__( self ):
        self.symbolCatalog = {klass.token: klass for klass in self.InstructionCatalog}

    def assemble_program( self, path ):
        statement_re = re.compile('[\s\t]*([a-zA-Z_]+)(?:[\s\t]+\[?([0-9]+)\]?)?(?:[\s\t]+#.*)?[\s\t]*\n')
        program = []
        with open(path, 'r') as infile:
            for line in infile:
                match = re.match(statement_re, line)
                if match is not None:
                    klass = self.symbolCatalog[match.group(1)]
                    if klass.has_argument:
                        instruction = klass(int(match.group(2)))
                    else:
                        instruction = klass()
                    program.append(instruction)
        return program
