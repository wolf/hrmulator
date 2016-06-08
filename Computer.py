from __future__ import print_function

from Assembler import Assembler

class ComputerError( Exception ): pass
class InboxIsEmptyError( ComputerError ): pass
class AccumulatorIsEmptyError( ComputerError ): pass
class MemoryTileIsEmptyError( ComputerError ): pass

class Computer:
    def __init__( self ):
        self.inbox = []
        self.outbox = []
        self.program_counter = None
        self.total_steps_executed = None
        self.program = []
        self.accumulator = None
        self.memory = {}
        self.break_points = {}

    def load_program( self, path ):
        asm = Assembler()
        self.program = asm.assemble_program(path)
        self.break_points = {}

    def dump_program( self, path ):
        with open(path, 'w+') as outfile:
            for instruction in self.program:
                outfile.write("{}\n".format(instruction))

    def print_program( self ):
        for i, instruction in enumerate(self.program):
            print("{}{}{:03d}: {}".format(
                '*' if self.break_points.get(i, False) else ' ',
                '@' if i==self.program_counter else ' ',
                i,
                instruction))

    def run_program( self ):
        self.program_counter = 0
        self.total_steps_executed = 0
        try:
            while self.program_counter < len(self.program):
                self.program[self.program_counter].execute(self)
        except InboxIsEmptyError:
            pass
        self.program_counter = None

    def is_running( self ):
        return program_counter is not None and 0 <= self.program_counter < len(self.program)

    def assertInboxIsNotEmpty( self ):
        if not len(self.inbox):
            raise InboxIsEmptyError()

    def assertAccumulatorIsNotEmpty( self ):
        if self.accumulator is None:
            raise AccumulatorIsEmptyError()

    def assertMemoryTileIsNotEmpty( self, tile_index ):
        if self.memory.get(tile_index, None) is None:
            raise MemoryTileIsEmptyError()






def main():
    computer = Computer()
    computer.inbox = ['B', 'O', 'O', 'T', 'S', 'E', 'Q', 'U', 'E', 'N', 'C', 'E']

    print()
    computer.load_program('programs/Busy_Mail_Room_speed.hrm')
    computer.print_program()
    print()

    computer.run_program()

    print(computer.outbox)
    print("Program size: {}; Total steps executed: {}".format(len(computer.program), computer.total_steps_executed))

if __name__ == '__main__':
    main()
