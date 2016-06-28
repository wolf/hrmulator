from collections import deque
from unittest import TestCase
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import hrmulator
from hrmulator.Memory import Memory, MemoryTileIsEmptyError


class TestInstructions(TestCase):

    def setUp(self):
        self.computer = Mock()
        self.computer.memory = Memory()
        self.computer.program_counter = 0
        self.computer.total_steps_executed = 0
        self.computer.program = []
        self.computer.jump_table = {}
        self.computer.inbox = deque([74])
        self.computer.outbox = []
        self.computer.accumulator = None

    def test_noop(self):
        noop = hrmulator.Instructions.NoOp()
        noop.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_move_from_inbox(self):
        move_from_inbox = hrmulator.Instructions.MoveFromInbox()
        move_from_inbox.execute(self.computer)
        self.assertEqual(self.computer.accumulator, 74)
        self.assertEqual(len(self.computer.inbox), 0)
        with self.assertRaises(hrmulator.Instructions.InboxIsEmptyError):
            move_from_inbox.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_move_to_outbox(self):
        move_to_outbox = hrmulator.Instructions.MoveToOutbox()
        with self.assertRaises(hrmulator.Instructions.AccumulatorIsEmptyError):
            move_to_outbox.execute(self.computer)
        self.computer.accumulator = 74
        move_to_outbox.execute(self.computer)
        self.assertIsNone(self.computer.accumulator)
        self.assertSequenceEqual(self.computer.outbox, [74])
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_copy_from(self):
        copy_from = hrmulator.Instructions.CopyFrom(0)
        with self.assertRaises(MemoryTileIsEmptyError):
            copy_from.execute(self.computer)
        self.computer.memory[0] = 74
        copy_from.execute(self.computer)
        self.assertEqual(self.computer.accumulator, 74)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_copy_from_indirect(self):
        copy_from = hrmulator.Instructions.CopyFrom(0, indirect=True)
        with self.assertRaises(MemoryTileIsEmptyError):
            copy_from.execute(self.computer)
        self.computer.memory[0] = 74
        with self.assertRaises(MemoryTileIsEmptyError):
            copy_from.execute(self.computer)
        self.computer.memory[74] = 5
        copy_from.execute(self.computer)
        self.assertEqual(self.computer.accumulator, 5)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_copy_to(self):
        copy_to = hrmulator.Instructions.CopyTo(0)
        with self.assertRaises(hrmulator.Instructions.AccumulatorIsEmptyError):
            copy_to.execute(self.computer)
        copy_to = hrmulator.Instructions.CopyTo('hello')
        self.computer.accumulator = 74
        with self.assertRaises(KeyError):
            copy_to.execute(self.computer)
        self.computer.memory.label_tile(0, 'hello')
        copy_to.execute(self.computer)
        self.assertEqual(self.computer.memory['hello'], 74)
        self.assertEqual(self.computer.accumulator, 74)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_copy_to_indirect(self):
        copy_to = hrmulator.Instructions.CopyTo('hello', indirect=True)
        self.computer.accumulator = 0
        self.computer.memory.label_tile(0, 'hello')
        with self.assertRaises(MemoryTileIsEmptyError):
            copy_to.execute(self.computer)
        self.computer.memory['hello'] = 74
        copy_to.execute(self.computer)
        self.assertEqual(self.computer.memory['hello'], 74)
        self.assertEqual(self.computer.memory[74], 0)
        self.assertEqual(self.computer.accumulator, 0)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_add(self):
        add = hrmulator.Instructions.Add(0)
        with self.assertRaises(hrmulator.Instructions.AccumulatorIsEmptyError):
            add.execute(self.computer)
        add = hrmulator.Instructions.Add('hello')
        self.computer.accumulator = 74
        with self.assertRaises(KeyError):
            add.execute(self.computer)
        self.computer.memory.label_tile(0, 'hello')
        with self.assertRaises(MemoryTileIsEmptyError):
            add.execute(self.computer)
        self.computer.memory['hello'] = 74
        add.execute(self.computer)
        self.assertEqual(self.computer.accumulator, 148)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_add_indirect(self):
        add = hrmulator.Instructions.Add('hello', indirect=True)
        self.computer.accumulator = 74
        self.computer.memory.label_tile(0, 'hello')
        self.computer.memory['hello'] = 2
        with self.assertRaises(MemoryTileIsEmptyError):
            add.execute(self.computer)
        self.computer.memory[2] = 26
        add.execute(self.computer)
        self.assertEqual(self.computer.accumulator, 100)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_subtract(self):
        subtract = hrmulator.Instructions.Subtract(0)
        with self.assertRaises(hrmulator.Instructions.AccumulatorIsEmptyError):
            subtract.execute(self.computer)
        subtract = hrmulator.Instructions.Subtract('hello')
        self.computer.accumulator = 74
        with self.assertRaises(KeyError):
            subtract.execute(self.computer)
        self.computer.memory.label_tile(0, 'hello')
        with self.assertRaises(MemoryTileIsEmptyError):
            subtract.execute(self.computer)
        self.computer.memory['hello'] = 74
        subtract.execute(self.computer)
        self.assertEqual(self.computer.accumulator, 0)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_bump_up(self):
        bump_up = hrmulator.Instructions.BumpUp('hello')
        with self.assertRaises(KeyError):
            bump_up.execute(self.computer)
        self.computer.memory.label_tile(0, 'hello')
        with self.assertRaises(MemoryTileIsEmptyError):
            bump_up.execute(self.computer)
        self.computer.memory[0] = 74
        bump_up.execute(self.computer)
        self.assertEqual(self.computer.memory['hello'], 75)
        self.assertEqual(self.computer.accumulator, 75)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_bump_down(self):
        bump_down = hrmulator.Instructions.BumpDown('hello')
        with self.assertRaises(KeyError):
            bump_down.execute(self.computer)
        self.computer.memory.label_tile(0, 'hello')
        with self.assertRaises(MemoryTileIsEmptyError):
            bump_down.execute(self.computer)
        self.computer.memory[0] = 74
        bump_down.execute(self.computer)
        self.assertEqual(self.computer.memory['hello'], 73)
        self.assertEqual(self.computer.accumulator, 73)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_jump_to(self):
        jump_to = hrmulator.Instructions.Jump(0)
        with self.assertRaises(hrmulator.Instructions.NoSuchJumpDestinationError):
            jump_to.execute(self.computer)
        jump_to = hrmulator.Instructions.Jump('hello')
        with self.assertRaises(hrmulator.Instructions.NoSuchJumpDestinationError):
            jump_to.execute(self.computer)
        self.computer.jump_table['hello'] = 0
        self.computer.program.append(jump_to)
        jump_to.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 0)
        self.assertEqual(self.computer.total_steps_executed, 1)

    def test_jump_if_zero_to(self):
        jump_if_zero_to = hrmulator.Instructions.JumpIfZero(0)
        with self.assertRaises(hrmulator.Instructions.AccumulatorIsEmptyError):
            jump_if_zero_to.execute(self.computer)
        self.computer.accumulator = 0
        with self.assertRaises(hrmulator.Instructions.NoSuchJumpDestinationError):
            jump_if_zero_to.execute(self.computer)
        jump_if_zero_to = hrmulator.Instructions.JumpIfZero('hello')
        with self.assertRaises(hrmulator.Instructions.NoSuchJumpDestinationError):
            jump_if_zero_to.execute(self.computer)
        self.computer.jump_table['hello'] = 0
        self.computer.program.append(jump_if_zero_to)
        jump_if_zero_to.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 0)
        self.assertEqual(self.computer.total_steps_executed, 1)
        self.computer.accumulator = 74
        jump_if_zero_to.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 2)

    def test_jump_if_negative_to(self):
        jump_if_negative_to = hrmulator.Instructions.JumpIfNegative(0)
        with self.assertRaises(hrmulator.Instructions.AccumulatorIsEmptyError):
            jump_if_negative_to.execute(self.computer)
        self.computer.accumulator = -74
        with self.assertRaises(hrmulator.Instructions.NoSuchJumpDestinationError):
            jump_if_negative_to.execute(self.computer)
        jump_if_negative_to = hrmulator.Instructions.JumpIfNegative('hello')
        with self.assertRaises(hrmulator.Instructions.NoSuchJumpDestinationError):
            jump_if_negative_to.execute(self.computer)
        self.computer.jump_table['hello'] = 0
        self.computer.program.append(jump_if_negative_to)
        jump_if_negative_to.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 0)
        self.assertEqual(self.computer.total_steps_executed, 1)
        self.computer.accumulator = 74
        jump_if_negative_to.execute(self.computer)
        self.assertEqual(self.computer.program_counter, 1)
        self.assertEqual(self.computer.total_steps_executed, 2)
