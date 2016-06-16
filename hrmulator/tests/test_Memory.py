from unittest import TestCase

import hrmulator


class TestMemory(TestCase):

    def setUp(self):
        self.memory = hrmulator.Memory()

    def test_memory_empty_lookup(self):
        self.assertIsNone(self.memory[0])

    def test_memory_set_and_get(self):
        self.memory[0] = 74
        self.assertEqual(self.memory[0], 74)

    def test_memory_apply_label(self):
        self.memory.label_tile(0, 'hello')
        self.assertIsNone(self.memory['hello'])

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
