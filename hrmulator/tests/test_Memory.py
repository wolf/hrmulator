from unittest import TestCase

import hrmulator
from hrmulator.Memory import (
    MemoryTileIsEmptyError,
    CantIndirectThroughLetter,
    CantStoreBadType
)


class TestMemory(TestCase):

    def setUp(self):
        self.memory = hrmulator.Memory()

    def test_memory_empty_lookup(self):
        with self.assertRaises(MemoryTileIsEmptyError):
            value = self.memory[0]

    def test_memory_empty_lookup_get(self):
        with self.assertRaises(MemoryTileIsEmptyError):
            value = self.memory.get(0)

    def test_memory_unknown_label(self):
        with self.assertRaises(KeyError):
            value = self.memory['hello']

    def test_memory_unknown_label_get(self):
        with self.assertRaises(KeyError):
            value = self.memory.get('hello')

    def test_memory_set_and_get(self):
        self.memory[0] = 74
        self.assertEqual(self.memory[0], 74)

    def test_memory_set_and_get_functions(self):
        self.memory.set(0, 74)
        self.assertEqual(self.memory.get(0), 74)

    def test_memory_apply_label(self):
        self.memory.label_tile(0, 'hello')
        with self.assertRaises(MemoryTileIsEmptyError):
            value = self.memory['hello']

    def test_memory_label_is_connected(self):
        self.memory.label_tile(0, 'hello')
        self.memory['hello'] = 74
        self.assertEqual(self.memory['hello'], 74)

    def test_memory_label_aliases_index(self):
        self.memory.label_tile(0, 'hello')
        self.memory[0] = 74
        self.assertEqual(self.memory[0], self.memory['hello'])
        self.assertEqual(self.memory['hello'], 74)

    def test_memory_multiple_labels(self):
        self.memory.label_tile(0, 'hello')
        self.memory.label_tile(0, 'goodbye')
        self.memory[0] = 74
        self.assertEqual(self.memory['goodbye'], self.memory['hello'])
        self.assertEqual(self.memory['goodbye'], 74)

    def test_memory_construct_with_values(self):
        m = hrmulator.Memory(values={0: 74})
        self.assertEqual(m[0], 74)

    def test_memory_construct_with_labels(self):
        m = hrmulator.Memory(labels={'hello': 0})
        m[0] = 74
        self.assertEqual(m['hello'], 74)

    def test_memory_construct_with_labels_and_values(self):
        m = hrmulator.Memory(labels={'hello': 0, 'goodbye': 0}, values={'hello': 74})
        self.assertEqual(m['hello'], 74)
        self.assertEqual(m[0], 74)
        self.assertEqual(m['hello'], m['goodbye'])

    def test_memory_empty_lookup_indirect(self):
        self.memory[0] = 74
        # self.memory[74] = None
        with self.assertRaises(MemoryTileIsEmptyError):
            value = self.memory.get(0, indirect=True)

    def test_memory_get_indirect(self):
        self.memory[0] = 74
        self.memory[74] = 'A'
        value = self.memory.get(0, indirect=True)
        self.assertEqual(value, 'A')

    def test_memory_set_indirect(self):
        self.memory[0] = 74
        value = self.memory.set(0, 'A', indirect=True)
        self.assertEqual(self.memory[74], 'A')

    def test_memory_get_indirect_through_letter(self):
        self.memory[0] = 'A'
        with self.assertRaises(CantIndirectThroughLetter):
            value = self.memory.get(0, indirect=True)

    def test_memory_set_indirect_through_letter(self):
        self.memory[0] = 'A'
        with self.assertRaises(CantIndirectThroughLetter):
            value = self.memory.set(0, 'A', indirect=True)

    def test_memory_set_bad_type(self):
        with self.assertRaises(CantStoreBadType):
            self.memory[0] = 'hello'
        with self.assertRaises(CantStoreBadType):
            self.memory.set(0, 5.2, indirect=True)
