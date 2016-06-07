from __future__ import print_function
import re

class ComputerError( Exception ): pass
class InboxIsEmptyError( ComputerError ): pass
class AccumulatorIsEmptyError( ComputerError ): pass
class MemoryTileIsEmptyError( ComputerError ): pass

class Computer:
    def __init__( self ):
        self.inbox = []
        self.outbox = []
        self.program_counter = None
        self.total_steps_executed = None
        self.program = []
        self.accumulator = None
        self.memory = {}
        self.break_points = {}

    def load_program( self, path ):
        asm = Assembler()
        self.program = asm.assemble_program(path)
        self.break_points = {}

    def dump_program( self, path ):
        with open(path, 'w+') as outfile:
            for instruction in self.program:
                outfile.write("{}\n".format(instruction))

    def print_program( self ):
        for i, instruction in enumerate(self.program):
            print("{}{}{:03d}: {}".format(
                '*' if self.break_points.get(i, False) else ' ',
                '@' if i==self.program_counter else ' ',
                i,
                instruction))

    def run_program( self ):
        self.program_counter = 0
        self.total_steps_executed = 0
        try:
            while self.program_counter < len(self.program):
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        self.program_counter = None

    def is_running( self ):
        return program_counter is not None and 0 <= self.program_counter < len(self.program)

    def assertInboxIsNotEmpty( self ):
        if not len(self.inbox):
            raise InboxIsEmptyError()

    def assertAccumulatorIsNotEmpty( self ):
        if self.accumulator is None:
            raise AccumulatorIsEmptyError()

    def assertMemoryTileIsNotEmpty( self, tile_index ):
        if self.memory.get(tile_index, None) is None:
            raise MemoryTileIsEmptyError()


class CPUInstruction:
    has_argument = False

    def __str__( self ):
        return self.token


class NoOp( CPUInstruction ):
    token = "no_op"

    def execute( self, computer ):
        computer.program_counter += 1
        computer.total_steps_executed += 1


class MoveFromInbox( CPUInstruction ):
    token = "move_from_inbox"

    def execute( self, computer ):
        computer.assertInboxIsNotEmpty()
        computer.accumulator = computer.inbox.pop()
        computer.program_counter += 1
        computer.total_steps_executed += 1


class MoveToOutbox( CPUInstruction ):
    token = "move_to_outbox"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.outbox.append(computer.accumulator)
        computer.accumulator = None
        computer.program_counter += 1
        computer.total_steps_executed += 1


class AbstractTileInstruction( CPUInstruction ):
    has_argument = True

    def __str__( self ):
        return "{} [{}]".format(self.token, self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index


class CopyTo( AbstractTileInstruction ):
    token = "copy_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.memory[self.tile_index] = computer.accumulator
        computer.program_counter += 1
        computer.total_steps_executed += 1


class CopyFrom( AbstractTileInstruction ):
    token = "copy_from"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Add( AbstractTileInstruction ):
    token = "add"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator += computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Subtract( AbstractTileInstruction ):
    token = "subtract"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator -= computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Jump( CPUInstruction ):
    token = "jump_to"
    has_argument = True

    def __str__( self ):
        return "{} {:03d}".format(self.token, self.destination_pc)

    def __init__( self, destination_pc ):
        self.destination_pc = destination_pc

    def execute( self, computer ):
        computer.program_counter = self.destination_pc
        computer.total_steps_executed += 1


class JumpIfZero( Jump ):
    token = "jump_if_zero_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator == 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1
        computer.total_steps_executed += 1


class JumpIfNegative( Jump ):
    token = "jump_if_negative_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator < 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1
        computer.total_steps_executed += 1


class BumpUp( AbstractTileInstruction ):
    token = "bump_up"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] += 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class BumpDown( AbstractTileInstruction ):
    token = "bump_down"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] -= 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1



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


def main():
    computer = Computer()
    computer.inbox = [1, -2, 3, -4, 5, -6]

    print()
    computer.load_program('programs/Absolute_Positivity.hrm')
    computer.break_points[3] = True
    computer.program_counter = 5
    computer.print_program()
    print()

    computer.run_program()

    print(computer.outbox)

if __name__ == '__main__':
    main()
