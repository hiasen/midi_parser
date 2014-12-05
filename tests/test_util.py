import unittest
import io
import util


class VariableLengthTest(unittest.TestCase):
    bytes_to_test = (
        (b'\x00', 0),
        (b'\x7f', 0x7f),
        (b'\x81\x48', 0xc8),
        (b'\xc0\x80\x00', 0x100000),
        (b'\xff\xff\xff\x7f', 0x0fffffff),
    )

    def test_read_variable_length(self):
        for bytes_, correct_number in self.bytes_to_test:
            stream = io.BytesIO(bytes_)
            number = util.read_variable_length_int(stream)
            self.assertEqual(number, correct_number,
                             "{} not equal {}".format(bytes_, correct_number))
            self.assertEqual(stream.tell(), len(bytes_))

    def test_int_to_variable_length(self):
        for bytes_, number in self.bytes_to_test:
            var_bytes = util.int_to_variable_bytes(number)
            self.assertEqual(var_bytes, bytes_,
                             "number={}".format(number))

    def test_prepend_length(self):
        length = 10
        data = b'\xff' * length
        my_bytes = util.prepend_length(data)
        self.assertEqual(my_bytes[1:], data)
        self.assertEqual(my_bytes[0], length)

        length = 128
        data = b'\xff' * length
        my_bytes = util.prepend_length(data)
        self.assertEqual(my_bytes[2:], data)
        self.assertEqual(my_bytes[:2], util.int_to_variable_bytes(length))


class BitOperationsTest(unittest.TestCase):

    def test_first_bit_and_rest(self):
        self.assertEqual(util.first_bit_and_rest(0xff), (1, 127))
        self.assertEqual(util.first_bit_and_rest(0x22), (0, 0x22))

    def test_nibbles(self):
        self.assertEqual(util.get_nibbles(0xff), (0xf, 0xf))
        self.assertEqual(util.get_nibbles(0x37), (0x3, 0x7))
        self.assertEqual(util.get_nibbles(0x00), (0x0, 0x0))
