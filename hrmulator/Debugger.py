from collections import deque
import readline
import re

from .Computer import Computer
from .Memory import Memory
from .Instructions import InboxIsEmptyError, Jump


class Debugger(Computer):

    set_or_clear_breakpoint_re = re.compile('^b ([0-9]+)$')

    def __init__(self):
        super().__init__()
        self.breakpoints = set({})
        self.temporary_breakpoints = {0}

    def adorn_line(self, step_number):
        prefix = '!' if step_number-1 in self.breakpoints else ' '
        suffix = super().adorn_line(step_number)
        return prefix + suffix

    def menu(self):
        while True:
            self.print_program(slice(self.program_counter, self.program_counter+1))
            command = input('% ')
            if command == 's':
                ins = self.program[self.program_counter]
                if isinstance(ins, Jump):
                    self.temporary_breakpoints.add(ins.lookup_destination(self))
                if type(ins) is not Jump:
                    self.temporary_breakpoints.add(self.program_counter+1)
                break
            elif command == 'c':
                return False
            elif command.startswith('b'):
                match = re.match(self.set_or_clear_breakpoint_re, command)
                if match is not None:
                    step_number = int(match.group(1))-1
                    if step_number in self.breakpoints:
                        self.breakpoints.remove(step_number)
                    else:
                        self.breakpoints.add(step_number)
            elif command == 'a':
                if self.memory.is_char(self.accumulator):
                    print("'{}'".format(self.accumulator))
                else:
                    print(self.accumulator)
            elif command == 'e':
                print('inbox:', end='')
                print(self.inbox, end='')
                if self.memory.is_char(self.accumulator):
                    format_str = "; accumulator:'{}'"
                else:
                    format_str = "; accumulator:{}"
                print(format_str.format(self.accumulator), end='')
                print('; outbox:', end='')
                print(self.outbox)
            elif command == 'i':
                print(self.inbox)
            elif command == 'o':
                print(self.outbox)
            elif command == 'l':
                self.print_program()
            elif command == 'm':
                self.memory.debug_print()
            elif command == 'q':
                return True
            elif command == '?':
                print("""Commands:
  a - print the accumulator
  b <number> - set or clear a breakpoint at step <number>
  c - continue running
  e - print everything: inbox, accumulator, and outbox
  i - print the inbox
  l - print a complete listing of the program
  m - print the contents of memory
  o - print the outbox
  q - quit immediately (abort the program)
  s - step
  ? - this help message""")
        return False

    def run(self):
        self.program_counter = 0
        self.total_steps_executed = 0
        if self.inbox is None:
            self.inbox = deque([])
        self.outbox = []
        escape = False
        try:
            while self.program_counter < len(self.program) and not escape:
                if self.program_counter in self.breakpoints.union(self.temporary_breakpoints):
                    self.temporary_breakpoints = set()
                    escape = self.menu()
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        if not escape:
            self.menu()
        self.program_counter = None

    def print_run_program(self, *,
            program_path=None,
            program_text=None,
            inbox=None,
            memory=None):
        self.program_counter = 0
        super().print_run_program(
            program_path=program_path,
            program_text=program_text,
            inbox=inbox,
            memory=memory)
