import re

from .Instructions import InstructionCatalog


class Assembler:
    def __init__(self):
        self.symbolCatalog = {ins.token: ins for ins in InstructionCatalog}

    def assemble_program(self, path):
        label_re = re.compile('([A-Z_]+):\s*\n?')
        statement_re = re.compile(
            '\s*([a-zA-Z_]+)(?:\s+\[?([0-9]+|[A-Z_]+)\]?)?(?:\s+#.*)?\s*\n?'
        )
        program = []
        jump_table = {}
        step = 0
        with open(path, 'r') as infile:
            for line in infile:
                # if it's a label, save it in the jump_table
                match = re.match(label_re, line)
                if match is not None:
                    jump_table[match.group(1)] = step
                    continue

                # if it's an instruction, append it to the program
                match = re.match(statement_re, line)
                if match is not None:
                    klass = self.symbolCatalog[match.group(1)]
                    if klass.has_argument:
                        arg = match.group(2)
                        try:
                            arg = int(arg)
                        except ValueError:
                            pass
                        instruction = klass(arg)
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
