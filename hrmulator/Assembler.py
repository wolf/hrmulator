import re

from collections import OrderedDict
from .Instructions import InstructionCatalog


class Assembler:
    def __init__(self):
        self.symbolCatalog = {ins.token: ins for ins in InstructionCatalog}

    def assemble_program_file(self, path):
        with open(path, 'r') as infile:
            lines = infile.readlines()
        return self.assemble_program(lines)

    def assemble_program_text(self, text):
        lines = text.split('\n')
        return self.assemble_program(lines)

    def assemble_program(self, lines):
        label_re = re.compile('([A-Z_]+):\s*\n?')
        statement_re = re.compile(
            '\s*([a-zA-Z_]+)(?:\s+\[?([0-9]+|[A-Za-z_]+)\]?)?(?:\s+#.*)?\s*\n?'
        )
        program = []

        jump_table = OrderedDict()
            # using an OrderedDict here makes the labels print in the right
            # order when there are multiple labels at the same point

        step = 0
        for line in lines:
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

        return (program, jump_table)
