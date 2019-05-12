from unittest import TestCase

from hrmulator import Computer, Memory


program_text = """
START:
    move_from_inbox
    copy_to A
    move_from_inbox
    copy_to B
    subtract A
    jump_if_negative_to A_GREATER_THAN_B

    copy_from B
    jump_to FINISH

A_GREATER_THAN_B:
    copy_from A
FINISH:
    move_to_outbox
    jump_to START
"""


class TestIntegration003(TestCase):
    def test_maximization_room(self):
        computer = Computer()
        computer.memory = Memory(labels={"A": 0, "B": 1})
        computer.set_inbox([3, 8, -9, -3, 2, 2, 4, -9])
        computer.load_program(program_text=program_text)
        computer.run()
        self.assertSequenceEqual(computer.outbox, [8, -3, 2, 4])
