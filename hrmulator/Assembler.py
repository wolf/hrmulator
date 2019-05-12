from collections import OrderedDict
import re

from .Instructions import INSTRUCTION_CATALOG


class AssemblerError(Exception):
    def __init__(self, line_number, text):
        self.line_number = line_number
        self.text = text

    def __str__(self):
        return '{}, line {}: "{}"'.format(self.description, self.line_number, self.text)


class ArgumentRequiredError(AssemblerError):
    description = "Instruction requires argument"


class UnexpectedArgumentError(AssemblerError):
    description = "Unexpected argument"


class UnknownInstructionError(AssemblerError):
    description = "Unknown instruction"


class SyntaxError(AssemblerError):
    description = "Syntax error"


class Assembler:
    """
    This is the class that turns text into an HRM program.

    The public interface is:

        Assembler.assemble_program_file(file_path)
        Assembler.assemble_program_text(str)

    Either your program is stored in the file-system somewhere, or else you
    provide it inline.  Your choice.  Both routines return a tuple of the
    program itself, and the jump table referring into it.
    """

    comment_re = re.compile("(.*)#.*")
    # keep anything to the left of the comment marker

    label_re = re.compile("(\w+):")
    instruction_with_arg_re = re.compile("(\w+)\s+(\w+)$")
    indirect_tile_instruction_re = re.compile("(\w+)\s+\[(\w+)\]$")
    # Note tile index is made of word characters not necessarily digits.

    instruction_re = re.compile("(\w+)$")

    def __init__(self):
        """
        Build a dictionary from Instruction.py's INSTRUCTION_CATALOG that
        maps symbols to the actual Instructions that implement them.
        """
        self.symbol_catalog = {ins.symbol: ins for ins in INSTRUCTION_CATALOG}

    def assemble_program_file(self, path):
        """...when your HRM program lives in the file-system."""
        with open(path, "r") as infile:
            lines = infile.readlines()
        return self._assemble_program(lines)

    def assemble_program_text(self, text):
        """...when your HRM program is provided inline."""
        lines = text.split("\n")
        return self._assemble_program(lines)

    def _assemble_program(self, lines):
        """Read the source line-by-line and translate it into instructions."""
        program = []

        jump_table = OrderedDict()
        # Maps labels to step numbers, 0-based, like program itself and
        # the program_counter.  We save the labels instead of resolving
        # them immediately to step numbers in the instructions because
        # we want to print them when we print the program.  Both the label
        # itself, and where it's the argument to a jump instruction.

        # Using an OrderedDict here makes the labels print in the right
        # order when there are multiple labels at the same point.  Edge
        # case, I know.

        step = 0
        line_number = 0 # ...for error reporting; 1-based like your editor.
        for line in lines:
            line_number += 1

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

            match = None
            arg = None
            indirect = False
            has_arg_match = re.match(self.instruction_with_arg_re, line)
            indirect_tile_match = re.match(self.indirect_tile_instruction_re, line)
            op_match = re.match(self.instruction_re, line)

            match = has_arg_match or indirect_tile_match
            if match is not None:
                arg = match.group(2)
                indirect = indirect_tile_match is not None
            else:
                match = op_match

            if match is not None:
                symbol = match.group(1).lower()
                if symbol not in self.symbol_catalog:
                    raise UnknownInstructionError(line_number, match.group(1))

                class_ = self.symbol_catalog[symbol]
                if class_.has_argument:
                    if arg is None:
                        raise ArgumentRequiredError(line_number, line)
                    try:
                        # arg could be a raw step number, or tile index.
                        arg = int(arg)
                    except ValueError:
                        # otherwise it's a name or label
                        pass

                    # Can't just say class_(arg, indirect=indirect) because it
                    # might be one of the jump instructions.  They don't take
                    # the indirect keyword
                    if indirect:
                        instruction = class_(arg, indirect=True)
                    else:
                        instruction = class_(arg)
                elif arg is not None:
                    raise UnexpectedArgumentError(line_number, arg)
                else:
                    instruction = class_()
                program.append(instruction)
                step += 1
            else:
                raise SyntaxError(line_number, line)

        return (program, jump_table)
