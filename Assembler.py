import re

from Instructions import InstructionCatalog


class Assembler:
    def __init__( self ):
        self.symbolCatalog = {klass.token: klass for klass in InstructionCatalog}

    def assemble_program( self, path ):
        label_re = re.compile('([A-Z_]+):\s*\n?')
        statement_re = re.compile('[\ \t]*([a-zA-Z_]+)(?:[\ \t]+\[?([0-9]+|[A-Z_]+)\]?)?(?:[\ \t]+#.*)?[\ \t]*\n?')
        program = []
        jump_table = {}
        step = 0
        with open(path, 'r') as infile:
            for line in infile:
                match = re.match(label_re, line)
                if match is not None:
                    jump_table[match.group(1)] = step
                    continue
                match = re.match(statement_re, line)
                if match is not None:
                    klass = self.symbolCatalog[match.group(1)]
                    if klass.has_argument:
                        instruction = klass(match.group(2))
                    else:
                        instruction = klass()
                    program.append(instruction)
                    step += 1

        # now let's step through the program and fixup all the symbolic jumps
        for instruction in program:
            target = getattr(instruction, 'destination_pc', None)
            if target is not None:
                if target in jump_table:
                    target = jump_table[target]
                else:
                    target = int(target)
                setattr(instruction, 'destination_pc', target)

        return program
