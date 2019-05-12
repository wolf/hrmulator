from unittest import TestCase

from hrmulator import Computer, Memory


program_text = """
START:
    move_from_inbox
    copy_to A
    move_from_inbox
    jump_if_zero_to ZERO
    copy_to B
    copy_to product

LOOP:
    bump_down A
    jump_if_zero_to DONE
    jump_if_negative_to ZERO
    copy_from B
    add product
    copy_to product
    jump_to LOOP

DONE:
    copy_from product
    jump_to OUTPUT
ZERO:
    copy_from zero
OUTPUT:
    move_to_outbox
    jump_to START
"""


class TestIntegration000(TestCase):
    def test_multiplication_workshop(self):
        computer = Computer()
        computer.memory = Memory(
            labels={"A": 0, "B": 1, "product": 2, "zero": 9}, values={"zero": 0}
        )
        computer.set_inbox([3, 2, 0, 7])
        computer.load_program(program_text=program_text)
        computer.run()
        self.assertSequenceEqual(computer.outbox, [6, 0])
