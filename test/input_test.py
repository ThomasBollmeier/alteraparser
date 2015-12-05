import unittest
import os
from alteraparser.io.string_input import StringInput
from alteraparser.io.file_input import FileInput


class StringInputTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_iteration(self):
        data_in = StringInput('Test')
        self.assertTrue(data_in.has_next_char())
        self.assertEqual(data_in.get_next_char(), 'T')
        self.assertEqual(data_in.get_next_char(), 'e')
        self.assertEqual(data_in.get_next_char(), 's')
        self.assertEqual(data_in.get_next_char(), 't')
        self.assertFalse(data_in.has_next_char())


class FileInputTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read(self):
        file_in = FileInput('input.txt')
        num_lines = 0
        while file_in.has_next_char():
            ch = file_in.get_next_char()
            if ch == os.linesep:
                num_lines += 1
            print(ch, end='')
        self.assertEqual(num_lines, 2)


if __name__ == "__main__":

    unittest.main()
