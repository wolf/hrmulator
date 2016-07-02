from collections import deque
import readline

from .Computer import Computer
from .Memory import Memory
from .Instructions import InboxIsEmptyError


class Debugger(Computer):

    def __init__(self):
        super().__init__()
        self.break_points = {}

    def menu(self):
        command = ''
        while command not in ('c', 'q'):
            command = input('% ')
            if command == 's':
                try:
                    self.program[self.program_counter].execute(self)
                except InboxIsEmptyError:
                    command = 'c'
            elif command == 'a':
                print(self.accumulator)
            elif command == 'e':
                print('inbox:', end='')
                print(self.inbox, end='')
                print('; accumulator:{}'.format(self.accumulator), end='')
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
            elif command == '?':
                print("""Commands:
  s - step
  a - print the accumulator
  e - print inbox, accumulator, and outbox
  i - print the inbox
  o - print the outbox
  l - print a complete listing of the program
  m - print the contents of memory
  ? - this help message""")
            if command != 'l':
                start = max(self.program_counter-3, 0)
                self.print_program(slice(start, self.program_counter+3))
        return command != 'q'


    def run(self):
        self.program_counter = 0
        self.total_steps_executed = 0
        if self.inbox is None:
            self.inbox = deque([])
        self.outbox = []
        try:
            escape = not self.menu()
            if not escape:
                while self.program_counter < len(self.program):
                    if self.program_counter in self.break_points:
                        self.menu()
                    self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        if not escape:
            self.menu()
        self.program_counter = None
