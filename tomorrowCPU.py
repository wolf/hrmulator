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
            print("{:03d}: {}".format(i, str(instruction)))

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
    def __str__( self ):
        return self.token()


class NoOp( CPUInstruction ):
    @classmethod
    def token( klass ):
        return "no_op"

    def execute( self, computer ):
        computer.program_counter += 1


class MoveFromInbox( CPUInstruction ):
    @classmethod
    def token( klass ):
        return "move_from_inbox"

    def execute( self, computer ):
        computer.assertInboxIsNotEmpty()
        computer.accumulator = computer.inbox.pop()
        computer.program_counter += 1


class MoveToOutbox( CPUInstruction ):
    @classmethod
    def token( klass ):
        return "move_to_outbox"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.outbox.append(computer.accumulator)
        computer.accumulator = None
        computer.program_counter += 1


class AbstractTileCommand( CPUInstruction ):
    def __str__( self ):
        return "{} [{}]".format(self.token(), self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index


class CopyTo( AbstractTileCommand ):
    @classmethod
    def token( klass ):
        return "copy_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.memory[self.tile_index] = computer.accumulator
        computer.program_counter += 1


class CopyFrom( AbstractTileCommand ):
    @classmethod
    def token( klass ):
        return "copy_from"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1


class AddFrom( AbstractTileCommand ):
    @classmethod
    def token( klass ):
        return "add_from"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator += computer.memory[self.tile_index]
        computer.program_counter += 1


class SubtractFrom( AbstractTileCommand ):
    @classmethod
    def token( klass ):
        return "subtract_from"

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator -= computer.memory[self.tile_index]
        computer.program_counter += 1


class Jump( CPUInstruction ):
    @classmethod
    def token( klass ):
        return "jump_to"

    def __str__( self ):
        return "{} {:03d}".format(self.token(), self.destination_pc)

    def __init__( self, destination_pc ):
        self.destination_pc = destination_pc

    def execute( self, computer ):
        computer.program_counter = self.destination_pc


class JumpIfZero( Jump ):
    @classmethod
    def token( klass ):
        return "jump_if_zero_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator == 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1


class JumpIfNegative( Jump ):
    @classmethod
    def token( klass ):
        return "jump_if_negative_to"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator < 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1


class BumpUp( AbstractTileCommand ):
    @classmethod
    def token( klass ):
        return "bump_up"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] += 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1


class BumpDown( AbstractTileCommand ):
    @classmethod
    def token( klass ):
        return "bump_down"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] -= 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1



def main():
    computer = Computer()
    computer.inbox = [1, -2, 3, -4, 5, -6]
    computer.program = [
        MoveFromInbox(),
        JumpIfNegative(3),
        Jump(6),
        CopyTo(0),
        SubtractFrom(0),
        SubtractFrom(0),
        MoveToOutbox(),
        Jump(0)
    ]
    print()
    computer.print_program()
    print()

    computer.run_program()

    print(computer.outbox)

if __name__ == '__main__':
    main()
