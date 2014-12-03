import unittest
import io

from util import read_variable_length, get_nibbles, first_bit_and_rest


class VariableLengthTest(unittest.TestCase):

    def test_read_variable_length(self):
        tests = (
            (b'\x00\x00', 0, 1),
            (b'\x00\xde', 0, 1),
            (b'\x7f\x11', 0x7f, 1),
            (b'\x80\x00', 0, 2),
            (b'\x81\x48', 0xc8, 2),
            (b'\xc0\x80\x00', 0x100000, 3),
            (b'\xff\xff\xff\x7f', 0x0fffffff, 4),
        )

        for bytes_, correct_number, bytes_read in tests:
            stream = io.BytesIO(bytes_)
            number = read_variable_length(stream)
            self.assertEqual(
                number,
                correct_number,
                "{} not equal {}".format(bytes_, correct_number))
            self.assertEqual(stream.tell(), bytes_read)


class BitOperationsTest(unittest.TestCase):

    def test_first_bit_and_rest(self):
        self.assertEqual(first_bit_and_rest(0xff), (1, 127))
        self.assertEqual(first_bit_and_rest(0x22), (0, 0x22))

    def test_nibbles(self):
        self.assertEqual(get_nibbles(0xff), (0xf, 0xf))
        self.assertEqual(get_nibbles(0x37), (0x3, 0x7))
        self.assertEqual(get_nibbles(0x00), (0x0, 0x0))
