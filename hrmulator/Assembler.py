import re

from collections import OrderedDict
from .Instructions import InstructionCatalog


class AssemblerError(Exception):
    pass


class ArgumentRequiredError(AssemblerError):
    pass


class UnknownSymbolError(AssemblerError):
    pass


class SyntaxError(AssemblerError):
    pass


class Assembler:

    comment_re = re.compile('(.*)#.*')
    label_re = re.compile('^(\w+):')
    tile_instruction_re = re.compile('^(\w+)\s+\[(\w+)\]')
    jump_instruction_re = re.compile('^(\w+)\s+(\w+)')
    instruction_re = re.compile('^(\w+)')

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
        program = []

        jump_table = OrderedDict()
            # using an OrderedDict here makes the labels print in the right
            # order when there are multiple labels at the same point

        step = 0
        for line in lines:
            # strip off the comment, if any
            match = re.match(self.comment_re, line)
            if match is not None:
                line = match.group(1)

            # strip off the whitespace, if any
            line = line.strip()
            # throw away blank lines
            if not line:
                continue

            # if it's a label, save it in the jump_table
            match = re.match(self.label_re, line)
            if match is not None:
                jump_table[match.group(1)] = step
                continue

            # does it match the instruction pattern
            match = None
            arg = None
            tile_match = re.match(self.tile_instruction_re, line)
            jump_match = re.match(self.jump_instruction_re, line)
            op_match = re.match(self.instruction_re, line)
            if tile_match is not None:
                match = tile_match
                arg = match.group(2)
            elif jump_match is not None:
                match = jump_match
                arg = match.group(2)
            else:
                match = op_match

            if match is not None:
                try:
                    klass = self.symbolCatalog[match.group(1).lower()]
                except KeyError:
                    raise UnknownSymbolError()

                if klass.has_argument:
                    if arg is None:
                        raise ArgumentRequiredError()
                    try:
                        arg = int(arg)
                    except ValueError:
                        pass
                    instruction = klass(arg)
                else:
                    instruction = klass()
                program.append(instruction)
                step += 1
            else:
                raise SyntaxError()

        return (program, jump_table)
