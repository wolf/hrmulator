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
