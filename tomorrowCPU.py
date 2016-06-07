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
        self.program = []
        self.accumulator = None
        self.memory = {}

    def run_program( self ):
        self.program_counter = 0
        try:
            while self.program_counter < len(self.program):
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        self.program_counter = None

    def is_running( self ):
        return program_counter is not None and 0 <= self.program_counter < len(self.program)

    def print_program( self ):
        for i, instruction in enumerate(self.program):
            print("{}{:03d}: {}".format('*' if i==self.program_counter else ' ', i, instruction))

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


class MoveFromInbox( CPUInstruction ):
    token = "move_from_inbox"

    def execute( self, computer ):
        computer.assertInboxIsNotEmpty()
        computer.accumulator = computer.inbox.pop()
        computer.program_counter += 1


class MoveToOutbox( CPUInstruction ):
    token = "move_to_outbox"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.outbox.append(computer.accumulator)
        computer.accumulator = None
        computer.program_counter += 1


class AbstractTileCommand( CPUInstruction ):
    has_argument = True

    def __str__( self ):
        return "{} [{}]".format(self.token, self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index


class CopyTo( AbstractTileCommand ):
    token = "copy_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.memory[self.tile_index] = computer.accumulator
        computer.program_counter += 1


class CopyFrom( AbstractTileCommand ):
    token = "copy_from"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1


class Add( AbstractTileCommand ):
    token = "add"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator += computer.memory[self.tile_index]
        computer.program_counter += 1


class Subtract( AbstractTileCommand ):
    token = "subtract"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator -= computer.memory[self.tile_index]
        computer.program_counter += 1


class Jump( CPUInstruction ):
    token = "jump_to"
    has_argument = True

    def __str__( self ):
        return "{} {:03d}".format(self.token, self.destination_pc)

    def __init__( self, destination_pc ):
        self.destination_pc = destination_pc

    def execute( self, computer ):
        computer.program_counter = self.destination_pc


class JumpIfZero( Jump ):
    token = "jump_if_zero_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator == 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1


class JumpIfNegative( Jump ):
    token = "jump_if_negative_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator < 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1


class BumpUp( AbstractTileCommand ):
    token = "bump_up"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] += 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1


class BumpDown( AbstractTileCommand ):
    token = "bump_down"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] -= 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1



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

    def load_program( self, path ):
        program = []
        with open(path, 'r') as infile:
            for line in infile:
                # parse with regexp
                # look up symbol in self.symbolCatalog
                # decide if it has an argument
                if klass.has_argument:
                    instruction = klass(argument)
                else:
                    instruction = klass()
                program.append(instruction)
        return program


def main():
    computer = Computer()
    computer.inbox = [1, -2, 3, -4, 5, -6]
    computer.program = [
        MoveFromInbox(),
        JumpIfNegative(3),
        Jump(6),
        CopyTo(0),
        Subtract(0),
        Subtract(0),
        MoveToOutbox(),
        Jump(0)
    ]
    print()
    computer.print_program()
    print()

    computer.run_program()

    print(computer.outbox)

    for instruction in Assembler.InstructionCatalog:
        print("{} {}".format(instruction.token, "#" if instruction.has_argument else ''))

    asm = Assembler()
    print(asm.symbolCatalog)

if __name__ == '__main__':
    main()
