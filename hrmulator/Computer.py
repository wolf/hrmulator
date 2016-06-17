"""
A very simple computer that executes programs assembled from instances of the
instructions implemented in Instructions.py.  Running such programs is easy,
the trouble we go to is in printing everything (and using a little color).
"""


from __future__ import print_function

from collections import defaultdict, deque

import colorama
import termcolor

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

    def load_program(self, program_path=None, program_text=None):
        asm = Assembler()
        if program_text is not None:
            self.program, self.jump_table = asm.assemble_program_text(program_text)
            self.program_path = 'inline'
        elif program_path is not None:
            self.program, self.jump_table = asm.assemble_program_file(program_path)
            self.program_path = program_path

    def print_program(self):
        # invert the jump table, so I can see where to print the labels
        labels = defaultdict(list)
        for label in self.jump_table:
            labels[self.jump_table[label]].append(label)

        # now step through the actual program: at each step...
        for i, instruction in enumerate(self.program):
            # print any labels that lead to this step;
            if i in labels:
                for label in labels[i]:
                    print('{}{}{}:'.format(
                        colorama.Fore.GREEN,
                        label,
                        colorama.Style.RESET_ALL
                    ))
            # then print the step number and the instruction at that step
            # (include markers for and noting the current step)
            print(" {}{}{:03d}:{} {}".format(
                '@' if i == self.program_counter else ' ',
                colorama.Style.DIM,
                i,
                colorama.Style.RESET_ALL,
                instruction.colored_str()))

    def run(self):
        self.program_counter = 0
        self.total_steps_executed = 0
        try:
            while self.program_counter < len(self.program):
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        self.program_counter = None

    def print_run_program(self, program_path=None, program_text=None, inbox=None, memory=None):
        if program_path is not None or program_text is not None:
            self.load_program(program_path=program_path, program_text=program_text)
        if inbox is not None:
            self.set_inbox(inbox)
        if memory is not None:
            self.memory = memory
        self.outbox = []

        print(self.program_path)
        print()
        self.print_program()
        print()

        printable_inbox = list(self.inbox)
            # copy our inbox, a deque, into a list; because
            # the deque will be consumed before we are ready to print

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
