from collections import deque
import readline
import re

from .Computer import Computer
from .Memory import Memory
from .Instructions import InboxIsEmptyError, Jump


class Debugger(Computer):

    command_with_argument_re = re.compile('^[a-z]\s*(\w+)$')

    def __init__(self):
        super().__init__()
        # breakpoints are held in sets, their elements are step indices into
        # self.program.  They number from 0, so they match the program_counter.
        self.breakpoints = set({})
        self.temporary_breakpoints = {0}

    def adorn_line(self, step_number):
        # step_number comes out of print_program, so it's off-by-one for the user
        prefix = '!' if step_number-1 in self.breakpoints else ' '
        suffix = super().adorn_line(step_number)
        return prefix + suffix

    def menu(self):
        ok_to_print_one_line = True
        command = None
        while True:
            if ok_to_print_one_line:
                self.print_program(slice(self.program_counter, self.program_counter+1))
            ok_to_print_one_line = True
            command = input('\ndebug> ')
            if command == 's':
                ###
                ### step
                ###
                ins = self.program[self.program_counter]
                if isinstance(ins, Jump):
                    # if it's a jump of any kind, break at the jump destination
                    self.temporary_breakpoints.add(ins.lookup_destination(self))
                if type(ins) is not Jump:
                    # if it's not an unconditional jump, break before the next instruction
                    self.temporary_breakpoints.add(self.program_counter+1)
                break
            elif command == 'c':
                ###
                ### continue
                ###
                return False
            elif command.startswith('b'):
                ###
                ### breakpoint
                ###
                match = re.match(self.command_with_argument_re, command)
                if match is None:
                    place = self.program_counter
                else:
                    place = match.group(1)

                if place in self.jump_table:
                    # locations in the jump_table already match the program_counter
                    place = self.jump_table[place]
                elif match is not None:
                    # remember, print_program numbers from 1, so if the user
                    # typed a number here, it is off-by-one; fix it
                    place = int(place)-1
                if place in self.breakpoints:
                    self.breakpoints.remove(place)
                else:
                    self.breakpoints.add(place)
            elif command == 'a':
                ###
                ### accumulator
                ###
                if self.memory.is_char(self.accumulator):
                    print("'{}'".format(self.accumulator))
                else:
                    print(self.accumulator)
            elif command == 'e':
                ###
                ### everything
                ###
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
                ###
                ### inbox
                ###
                printable_inbox = list(self.inbox or [])
                print(printable_inbox)
            elif command == 'o':
                ###
                ### outbox
                ###
                print(self.outbox)
            elif command.startswith('l'):
                ###
                ### list
                ###
                match = re.match(self.command_with_argument_re, command)
                if match is None:
                    slice_to_print = None
                else:
                    slice_to_print = slice(
                        self.program_counter,
                        self.program_counter + int(match.group(1))
                    )
                self.print_program(slice_to_print)
                ok_to_print_one_line = False
            elif command.startswith('m'):
                ###
                ### memory
                ###
                match = re.match(self.command_with_argument_re, command)
                if match is None:
                    self.memory.debug_print()
                else:
                    key = match.group(1)
                    try:
                        key = int(key)
                    except ValueError:
                        pass
                    self.memory.debug_print(key)
            elif command == 'q':
                ###
                ### quit
                ###
                return True
            elif command == '?':
                ###
                ### help
                ###
                print("""Commands:
  a - print the accumulator: the value you are currently holding
  b <number> - set or clear a breakpoint at step <number>
  c - continue running until the next breakpoint (if any)
  e - print everything: inbox, accumulator, and outbox
  i - print the inbox
  l - print a complete listing of the program
  l <number> print the next <number> lines of the program
  m - print every value in memory
  m <place> - print a specific value from memory
  o - print the outbox
  q - stop executing the program, and leave the debugger
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
            print()
            print('Program ran to completion.  Post-mortem:')
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
