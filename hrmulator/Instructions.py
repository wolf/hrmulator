import colorama
import termcolor

"""
These are the individual instructions which the Computer can execute.  They
have intimate knowledge of the computer and do things like directly update the
accumulator and the program_counter.  There are 12 concrete instructions:

    exported class name     assembler symbol

    NoOp                    no_op
    MoveFromInbox           move_from_inbox
    MoveToOutbox            move_to_outbox
    CopyFrom                copy_from
    CopyTo                  copy_to
    Add                     add
    Subtract                subtract
    BumpUp                  bump_up
    BumpDown                bump_down
    Jump                    jump_to
    JumpIfZero              jump_if_zero_to
    JumpIfNegative          jump_if_negative_to

In each case the class variable `token` is used both for printing and for the
symbol lookup needed in the assembler.  The `execute` function does the main
work.  `__init__` and `has_argument` cooperate to collect the argument in the
assembler.  The `__str__` function does the job of building a printable and
machine readable instruction out of `token`.

"""


class AbstractInstruction:
    """Base class for all instructions."""
    has_argument = False

    def __str__(self):
        return self.token

    def colored_str(self):
        return self.__str__()


class NoOp(AbstractInstruction):
    """
    Do nothing.

    Counts as a step executed when evaluating the optimization challenges.
    """
    token = "no_op"

    def execute(self, computer):
        computer.program_counter += 1
        computer.total_steps_executed += 1


class MoveFromInbox(AbstractInstruction):
    """
    Pop a value off the inbox and put it in the accumulator.

    The old value of the accumulator is discarded.  If the inbox is empty, an
    exception is thrown that nicely terminates this run of the (inner)
    program.  That is, it does _not_ terminate this Python script: it
    terminates the inner hrm program.
    """
    token = "move_from_inbox"

    def execute(self, computer):
        computer.assertInboxIsNotEmpty()
        computer.accumulator = computer.inbox.popleft()
        computer.program_counter += 1
        computer.total_steps_executed += 1


class MoveToOutbox(AbstractInstruction):
    token = "move_to_outbox"

    def execute(self, computer):
        computer.assertAccumulatorIsNotEmpty()
        computer.outbox.append(computer.accumulator)
        computer.accumulator = None
        computer.program_counter += 1
        computer.total_steps_executed += 1


class AbstractTileInstruction(AbstractInstruction):
    has_argument = True

    def __str__(self):
        return "{} [{}]".format(self.token, self.tile_index)

    def colored_str(self):
        tile_str = termcolor.colored(str(self.tile_index), 'blue')
        return "{} [{}]".format(self.token, tile_str)

    def __init__(self, tile_index):
        self.tile_index = tile_index


class CopyFrom(AbstractTileInstruction):
    token = "copy_from"

    def execute(self, computer):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class CopyTo(AbstractTileInstruction):
    token = "copy_to"

    def execute(self, computer):
        computer.assertAccumulatorIsNotEmpty()
        computer.memory[self.tile_index] = computer.accumulator
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Add(AbstractTileInstruction):
    token = "add"

    def execute(self, computer):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator += computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Subtract(AbstractTileInstruction):
    token = "subtract"

    def execute(self, computer):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.accumulator -= computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class BumpUp(AbstractTileInstruction):
    """
    Increment the value in a given memory tile by 1, and copy it into the
    accumulator.
    """
    token = "bump_up"

    def __init__(self, tile_index):
        self.tile_index = tile_index

    def execute(self, computer):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] += 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class BumpDown(AbstractTileInstruction):
    """
    Decrement the value in a given memory tile by 1, and copy it into the
    accumulator.
    """
    token = "bump_down"

    def __init__(self, tile_index):
        self.tile_index = tile_index

    def execute(self, computer):
        computer.assertMemoryTileIsNotEmpty(self.tile_index)
        computer.memory[self.tile_index] -= 1
        computer.accumulator = computer.memory[self.tile_index]
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Jump(AbstractInstruction):
    """Jump (unconditionally) to the supplied program step."""
    token = "jump_to"
    has_argument = True

    def __str__(self):
        try:
            result = "{} {:03d}".format(self.token, self.destination_pc)
        except ValueError:
            result = "{} {}{}{}".format(
                self.token,
                colorama.Fore.GREEN,
                self.destination_pc,
                colorama.Style.RESET_ALL
            )
        return result

    def __init__(self, destination_pc):
        self.destination_pc = destination_pc

    def lookup_destination(self, computer):
        result = self.destination_pc
        if result in computer.jump_table:
            result = computer.jump_table[result]
        return result

    def execute(self, computer):
        computer.program_counter = self.lookup_destination(computer)
        computer.total_steps_executed += 1


class JumpIfZero(Jump):
    """
    Jump if and only if the accumulator == 0 to the supplied program step.
    """
    token = "jump_if_zero_to"

    def execute(self, computer):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator == 0:
            computer.program_counter = self.lookup_destination(computer)
        else:
            computer.program_counter += 1
        computer.total_steps_executed += 1


class JumpIfNegative(Jump):
    """
    Jump if and only if the accumulator is less than zero to the supplied
    program step.

    Note: it is a fatal error if the value in the accumulator is not
    comparable to zero.
    """
    token = "jump_if_negative_to"

    def execute(self, computer):
        computer.assertAccumulatorIsNotEmpty()
        if computer.accumulator < 0:
            computer.program_counter = self.lookup_destination(computer)
        else:
            computer.program_counter += 1
        computer.total_steps_executed += 1


InstructionCatalog = [
    NoOp,
    MoveFromInbox,
    MoveToOutbox,
    CopyFrom,
    CopyTo,
    Add,
    Subtract,
    BumpUp,
    BumpDown,
    Jump,
    JumpIfZero,
    JumpIfNegative
]
