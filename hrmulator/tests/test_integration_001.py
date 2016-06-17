from unittest import TestCase

from hrmulator import Computer, Memory


exclusive_lounge = """
    jump_to START
SAME:
    copy_from [4]
FINISH:
    move_to_outbox
START:
    move_from_inbox
    jump_if_negative_to A_IS_NEGATIVE
A_IS_POSITIVE:
    move_from_inbox
    jump_if_negative_to DIFFERENT
    jump_to SAME
A_IS_NEGATIVE:
    move_from_inbox
    jump_if_negative_to SAME
DIFFERENT:
    copy_from [5]
    jump_to FINISH
"""

class TestIntegration001(TestCase):
    def test_exclusive_lounge(self):
        self.computer = Computer()
        self.computer.memory = Memory(values={4:0, 5:1})
        self.computer.set_inbox([-2, -8, 3, -5, -3, 7, 4, 3])
        self.computer.load_program(program_text=exclusive_lounge)
        self.computer.run()
        self.assertSequenceEqual(self.computer.outbox, [0, 1, 1, 0])
