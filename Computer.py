from __future__ import print_function

from collections import defaultdict, deque
from .Assembler import Assembler


class ComputerError(Exception):
    pass


class InboxIsEmptyError(ComputerError):
    pass


class AccumulatorIsEmptyError(ComputerError):
    pass


class MemoryTileIsEmptyError(ComputerError):
    pass


class Computer:
    def __init__(self):
        self.program_counter = None
        self.total_steps_executed = None
        self.accumulator = None
        self.memory = {}
        self.break_points = {}
        self.program_path = None
        self.program = None
        self.jump_table = None
        self.inbox = None
        self.outbox = None

    def set_inbox(self, inbox):
        self.inbox = deque(inbox)

    def load_program(self, path):
        asm = Assembler()
        self.program, self.jump_table = asm.assemble_program(path)
        self.program_path = path
        self.break_points = {}

    def dump_program(self, path):
        with open(path, 'w+') as outfile:
            for instruction in self.program:
                outfile.write("{}\n".format(instruction))

    def print_program(self):
        labels = defaultdict(list)
        for label in self.jump_table:
            labels[self.jump_table[label]].append(label)

        for i, instruction in enumerate(self.program):
            if i in labels:
                for label in labels[i]:
                    print('{}:'.format(label))
            print("{}{}{:03d}: {}".format(
                '*' if self.break_points.get(i, False) else ' ',
                '@' if i == self.program_counter else ' ',
                i,
                instruction))

    def run(self):
        self.program_counter = 0
        self.total_steps_executed = 0
        try:
            while self.program_counter < len(self.program):
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        self.program_counter = None

    def print_run_program(self, program_path=None, inbox=None):
        if program_path is not None:
            self.load_program(program_path)
        if inbox is not None:
            self.set_inbox(inbox)
        self.outbox = []

        print(self.program_path)
        print()
        self.print_program()
        print()

        printable_inbox = list(self.inbox)

        self.run()

        print("Inbox:")
        print(printable_inbox)
        print("Outbox:")
        print(self.outbox)
        print()
        print("Program size: {}; Total steps executed: {}".format(
            len(self.program),
            self.total_steps_executed
        ))

    def is_running(self):
        return (self.program_counter is not None and
                0 <= self.program_counter < len(self.program))

    def assertInboxIsNotEmpty(self):
        if not len(self.inbox):
            raise InboxIsEmptyError()

    def assertAccumulatorIsNotEmpty(self):
        if self.accumulator is None:
            raise AccumulatorIsEmptyError()

    def assertMemoryTileIsNotEmpty(self, tile_index):
        if self.memory.get(tile_index, None) is None:
            raise MemoryTileIsEmptyError()
