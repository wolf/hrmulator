from unittest import TestCase

import hrmulator


class TestAssembler(TestCase):
    def setUp(self):
        self.assembler = hrmulator.Assembler.Assembler()

    def test_assembles_correct_program(self):
        good_assembly = """START:
            move_from_inbox
            move_to_outbox
            jump_to START"""
        program, jump_table = self.assembler.assemble_program_text(good_assembly)
        self.assertEqual(len(program), 3)
        self.assertEqual(len(jump_table), 1)
        self.assertEqual(jump_table["START"], 0)
        self.assertIsInstance(program[0], hrmulator.Instructions.MoveFromInbox)
        self.assertIsInstance(program[1], hrmulator.Instructions.MoveToOutbox)
        self.assertIsInstance(program[2], hrmulator.Instructions.Jump)
        self.assertEqual(program[2].destination_pc, "START")

    def test_raises_argument_required(self):
        bad_assembly = """copy_from"""
        with self.assertRaises(hrmulator.Assembler.ArgumentRequiredError):
            program, jump_table = self.assembler.assemble_program_text(bad_assembly)

    def test_raises_unexpected_argument(self):
        bad_assembly = """move_from_inbox 2"""
        with self.assertRaises(hrmulator.Assembler.UnexpectedArgumentError):
            program, jump_table = self.assembler.assemble_program_text(bad_assembly)

    def test_raises_unknown_instruction(self):
        bad_assembly = """move_from"""
        with self.assertRaises(hrmulator.Assembler.UnknownInstructionError):
            program, jump_table = self.assembler.assemble_program_text(bad_assembly)

    def test_raises_syntax_error(self):
        bad_assembly = """; gorf forble gitz"""
        with self.assertRaises(hrmulator.Assembler.SyntaxError):
            program, jump_table = self.assembler.assemble_program_text(bad_assembly)
