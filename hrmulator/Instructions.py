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


import colorama
import termcolor


class InstructionError(Exception):
    pass


class InboxIsEmptyError(InstructionError):
    pass


class AccumulatorIsEmptyError(InstructionError):
    pass


class IncompatibleTypesError(InstructionError):
    pass


class NoSuchJumpDestinationError(InstructionError):
    pass


class AbstractInstruction:
    """Base class for all instructions."""
    has_argument = False

    def __str__(self):
        return self.token

    def colored_str(self):
        return self.__str__()

    def assertAccumulatorIsNotEmpty(self, computer):
        if computer.accumulator is None:
            raise AccumulatorIsEmptyError('The accumulator is empty.')


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
        if computer.inbox is None or not len(computer.inbox):
            raise InboxIsEmptyError('The inbox is empty.')
        computer.accumulator = computer.inbox.popleft()
        computer.program_counter += 1
        computer.total_steps_executed += 1


class MoveToOutbox(AbstractInstruction):
    token = "move_to_outbox"

    def execute(self, computer):
        self.assertAccumulatorIsNotEmpty(computer)
        computer.outbox.append(computer.accumulator)
        computer.accumulator = None
        computer.program_counter += 1
        computer.total_steps_executed += 1


class AbstractTileInstruction(AbstractInstruction):
    has_argument = True

    def __str__(self):
        s = "{} [{}]" if self.indirect else "{} {}"
        return s.format(self.token, self.tile_index)

    def colored_str(self):
        tile_str = termcolor.colored(str(self.tile_index), 'blue')
        s = "{} [{}]" if self.indirect else "{} {}"
        return s.format(self.token, tile_str)

    def __init__(self, tile_index, indirect=False):
        self.indirect = indirect
        self.tile_index = tile_index

    def is_char(self, value):
        return type(value)==str and len(value)==1


class CopyFrom(AbstractTileInstruction):
    token = "copy_from"

    def execute(self, computer):
        computer.accumulator = computer.memory.get(self.tile_index, self.indirect)
        computer.program_counter += 1
        computer.total_steps_executed += 1


class CopyTo(AbstractTileInstruction):
    token = "copy_to"

    def execute(self, computer):
        self.assertAccumulatorIsNotEmpty(computer)
        computer.memory.set(self.tile_index, computer.accumulator, self.indirect)
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Add(AbstractTileInstruction):
    token = "add"

    def execute(self, computer):
        self.assertAccumulatorIsNotEmpty(computer)
        value_to_add = computer.memory.get(self.tile_index, self.indirect)
        if self.is_char(value_to_add) or self.is_char(computer.accumulator):
            raise IncompatibleTypesError("You can't add a letter.  What would that even mean?")
        computer.accumulator += value_to_add
        computer.program_counter += 1
        computer.total_steps_executed += 1


class Subtract(AbstractTileInstruction):
    token = "subtract"

    def execute(self, computer):
        self.assertAccumulatorIsNotEmpty(computer)
        value_to_subtract = computer.memory.get(self.tile_index, self.indirect)
        value_to_subtract_is_char = self.is_char(value_to_subtract)
        if value_to_subtract_is_char != self.is_char(computer.accumulator):
            raise IncompatibleTypesError("You can't subtract (from) a letter.  What would that even mean?")
        if value_to_subtract_is_char:
            value_to_subtract = ord(value_to_subtract)
            computer.accumulator = ord(computer.accumulator)
        computer.accumulator -= value_to_subtract
        computer.program_counter += 1
        computer.total_steps_executed += 1


class BumpUp(AbstractTileInstruction):
    """
    Increment the value in a given memory tile by 1, and copy it into the
    accumulator.
    """
    token = "bump_up"

    def execute(self, computer):
        value = computer.memory.get(self.tile_index, self.indirect) + 1
        if self.is_char(value):
            raise IncompatibleTypesError("You can't add to a letter.  What would that even mean?")
        computer.memory.set(self.tile_index, value, self.indirect)
        computer.accumulator = value
        computer.program_counter += 1
        computer.total_steps_executed += 1


class BumpDown(AbstractTileInstruction):
    """
    Decrement the value in a given memory tile by 1, and copy it into the
    accumulator.
    """
    token = "bump_down"

    def execute(self, computer):
        value = computer.memory.get(self.tile_index, self.indirect) - 1
        if self.is_char(value):
            raise IncompatibleTypesError("You can't subtract from a letter.  What would that even mean?")
        computer.memory.set(self.tile_index, value, self.indirect)
        computer.accumulator = value
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
        if type(result) is not int:
            raise NoSuchJumpDestinationError(result,
                'The label "{}" does not appear in the program.'.format(result)
            )
        elif not 0<=result<len(computer.program):
            raise NoSuchJumpDestinationError(result,
                'Step number {} is outside the range of the program.'.format(result)
            )
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
        self.assertAccumulatorIsNotEmpty(computer)
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
        self.assertAccumulatorIsNotEmpty(computer)
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
