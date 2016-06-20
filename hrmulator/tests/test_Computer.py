from unittest import TestCase

import hrmulator


class TestComputer(TestCase):

    def setUp(self):
        self.computer = hrmulator.Computer()

    def test_missing_inbox(self):
        self.computer.load_program(
            program_text="""
                START:
                    move_from_inbox
                    move_to_outbox
                    jump_to START"""
        )
        self.computer.run()
        self.assertSequenceEqual(self.computer.outbox, [])

    def test_missing_inbox_printable(self):
        self.computer.print_run_program(
            program_text="""
                START:
                    move_from_inbox
                    move_to_outbox
                    jump_to START"""
        )
        self.assertSequenceEqual(self.computer.outbox, [])
