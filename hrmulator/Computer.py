"""
A very simple computer that executes programs assembled from instances of the
instructions implemented in Instructions.py.  Running such programs is easy,
the trouble we go to is in printing everything (and using a little color).
"""
from collections import defaultdict, deque

import colorama

from .Assembler import Assembler
from .Memory import Memory
from .Instructions import InboxIsEmptyError


class Computer:
    def __init__(self):
        self.program_counter = None
        self.total_steps_executed = None
        self.accumulator = None
        self.memory = Memory()
        self.program_path = None
        self.program = None
        self.jump_table = None
        self.inbox = None
        self.outbox = None

    def set_inbox(self, inbox):
        self.inbox = deque(inbox)

    def load_program(self, *, program_path=None, program_text=None):
        asm = Assembler()
        if program_text is not None:
            self.program, self.jump_table = asm.assemble_program_text(program_text)
            self.program_path = "inline"
        elif program_path is not None:
            self.program, self.jump_table = asm.assemble_program_file(program_path)
            self.program_path = program_path

    def _print_line(self, step_number, instruction):
        """
        Return a prefix for an individual line of the program listing that shows
        anything interesting there.

        Meant to be overridden by sub-classes. E.g., Computer puts an '@' on
        the line where the program counter is; Debugger puts a '!' on any line
        that has a breakpoint.
        """

        # `step_number` here comes from `print_program` so it's off-by-one for the user
        print(
            "   {}{}{:03d}:{} {}".format(
                "@" if step_number - 1 == self.program_counter else " ",
                colorama.Style.DIM,
                step_number,
                colorama.Style.RESET_ALL,
                instruction.colored_str(),
            )
        )

    def _print_label(self, step_number, label):
        print(f"{colorama.Fore.GREEN}{label}{colorama.Style.RESET_ALL}:")

    def print_program(self, slice_to_print=None):
        # invert the jump table, so I can see where to print the labels
        labels = defaultdict(list)
        for label in self.jump_table:
            # we print instruction indices off by one, and lookup the label with the off-by-one
            # index, so make sure the label is off by one to match
            labels[self.jump_table[label] + 1].append(label)

        # If you want to print just a single line of the program, provide
        # a slice of size 1.
        if type(slice_to_print) is slice:
            program_chunk = self.program.__getitem__(slice_to_print)
            offset = slice_to_print.start
        else:
            program_chunk = self.program
            offset = 0

        # now step through the actual program: at each step...
        for i, instruction in enumerate(program_chunk, offset + 1):
            # print any labels that lead to this step;
            if i in labels:
                for label in labels[i]:
                    self._print_label(i, label)
            self._print_line(i, instruction)

    def run(self):
        self.program_counter = 0
        self.total_steps_executed = 0
        if self.inbox is None:
            self.inbox = deque([])
        self.outbox = []
        try:
            while self.program_counter < len(self.program):
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        self.program_counter = None

    def print_run_program(self, *, program_path=None, program_text=None, inbox=None, memory=None):
        if program_path is not None or program_text is not None:
            self.load_program(program_path=program_path, program_text=program_text)
        if inbox is not None:
            self.set_inbox(inbox)
        if memory is not None:
            self.memory = memory

        print(self.program_path)
        print()
        self.print_program()
        print()

        printable_inbox = list(self.inbox or [])
        # copy our inbox, a deque, into a list; because
        # the deque will be consumed before we are ready to print

        self.run()

        print("Inbox:")
        print(printable_inbox)
        print("Outbox:")
        print(self.outbox)
        print()
        print("Program size: {len(self.program)}; Total steps executed: {self.total_steps_executed}")
