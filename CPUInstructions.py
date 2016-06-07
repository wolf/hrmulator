"""
These are the individual instructions which the Computer can execute.  They
have intimate knowledge of the computer and do things like directly update the
accumulator and the program_counter.  There are 12 concrete instructions:

    exported class name     assembler symbol

    NoOp                    no_op
    MoveFromInbox           move_from_inbox
    MoveToOutbox            move_to_outbox
    CopyTo                  copy_to
    CopyFrom                copy_from
    Add                     add
    Subtract                subtract
    Jump                    jump_to
    JumpIfZero              jump_if_zero_to
    JumpIfNegative          jump_if_negative_to
    BumpUp                  bump_up
    BumpDown                bump_down

In each case the class variable `token` is used both for printing and for the
symbol lookup needed in the assembler.  The `execute` function does the main
work.  `__init__` and `has_argument` cooperate to collect the argument in the
assembler.  The `__str__` function does the job of building a printable and
machine readable instruction out of `token`.

"""

class CPUInstruction:
    has_argument = False

    def __str__( self ):
        return self.token


class NoOp( CPUInstruction ):
    """Do nothing.  Counts as a step executed when evaluating the optimization challenges."""
    token = "no_op"

    def execute( self, computer ):
        computer.program_counter += 1
        computer.total_steps_executed += 1


class MoveFromInbox( CPUInstruction ):
    """
    Pop a value off the inbox and put it in the accumulator.

    The old value of the accumulator is discarded.  If the inbox is empty, an
    exception is thrown that nicely terminates this run of the (inner)
    program.  That is, it does _not_ terminate this Python script: it
    terminates the inner hrm program.
    """
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
    """Increment the value in a given memory tile by 1, and copy it into the accumulator."""
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
    """Decrement the value in a given memory tile by 1, and copy it into the accumulator."""
    token = "bump_down"

    def __init__( self, tile_index ):
        self.tile_index = tile_index

    def execute( self, computer ):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] -= 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1
