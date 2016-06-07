# 'bump + <tile>'
# 'bump - <tile>'

class ComputerError( Exception ): pass
class InboxIsEmptyError( ComputerError ): pass
class AccumulatorIsEmptyError( ComputerError ): pass
class MemoryTileIsEmptyError( ComputerError ): pass

class Computer:
    def __init__( self ):
        self.inbox = []
        self.outbox = []
        self.program_counter = 0
        self.program = []
        self.accumulator = None
        self.memory = {}

    def run_program( self ):
        self.program_counter = 0
        while self.program_counter < len(self.program):
            self.program[self.program_counter].execute(self)

    def assertInboxIsNotEmpty( self ):
        if not len(self.inbox):
            raise InboxIsEmptyError()

    def assertAccumulatorIsNotEmpty( self ):
        if self.accumulator is None:
            raise AccumulatorIsEmptyError()

    def assertMemoryTileIsNotEmpty( self, tile_index ):
        if self.memory.get(tile_index, None) is None:
            raise MemoryTileIsEmptyError()

class CPUInstruction: pass


class NoOp( CPUInstruction ):
    def __str__( self ):
        return "no_op"

    def execute( self, computer ):
        computer.program_counter += 1


class MoveFromInbox( CPUInstruction ):
    def __str__( self ):
        return "move_from_inbox"

    def execute( self, computer ):
        computer.assertInboxIsNotEmpty()
        computer.accumulator = computer.inbox.pop()
        computer.program_counter += 1


class MoveToOutbox( CPUInstruction ):
    def __str__( self ):
        return "move_to_outbox"

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.outbox.append(computer.accumulator)
        computer.accumulator = None
        computer.program_counter += 1


class CopyTo( CPUInstruction ):
    def __str__( self ):
        return "copy_to [{}]".format(self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        computer.memory[self.tile_index] = computer.accumulator
        computer.program_counter += 1


class CopyFrom( CPUInstruction ):
    def __str__( self ):
        return "copy_from [{}]".format(self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1


class AddFrom( CPUInstruction ):
    def __str__( self ):
        return "add_from [{}]".format(self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator += computer.memory[self.tile_index]
        computer.program_counter += 1


class SubtractFrom( CPUInstruction ):
    def __str__( self ):
        return "subtract_from [{}]".format(self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator -= computer.memory[self.tile_index]
        computer.program_counter += 1


class Jump( CPUInstruction ):
    def __str__( self ):
        return "jump_to {:03d}".format(self.destination_pc)

    def __init__( self, destination_pc ):
        self.destination_pc = destination_pc

    def execute( self, computer ):
        computer.program_counter = self.destination_pc


class JumpIfZero( Jump ):
    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator == 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1


class JumpIfNegative( Jump ):
    def execute( self, computer ):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator < 0:
            computer.program_counter = self.destination_pc
        else:
            computer.program_counter += 1


class BumpUp( CPUInstruction ):
    def __str__( self ):
        return "bump_up [{}]".format(self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] += 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1


class BumpDown( CPUInstruction ):
    def __str__( self ):
        return "bump_down [{}]".format(self.tile_index)

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] -= 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1



def main():
    computer = Computer()
    computer.inbox = [1, 2, 3, 4, 5, 6]
    computer.program = [
        MoveFromInbox(),
        MoveToOutbox(),
        Jump(0)
    ]
    for i, instruction in enumerate(computer.program):
        print("{:03d}: {}".format(i, str(instruction)))

    try:
        computer.run_program()
    except InboxIsEmptyError:
        pass

    print(computer.outbox)

if __name__ == '__main__':
    main()
