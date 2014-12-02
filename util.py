"""Utility functions for parsing midi events and midi-files."""


def get_nibbles(byte):
    """Returns the two nibbles of a byte."""
    return (byte & 0xf0) >> 4, byte & 0xf


def first_bit_and_rest(byte):
    return bool(byte & 0x80), byte & 0x7f


def single_byte_iterator(stream):
    """Gives one byte at a time from stream."""
    byte = stream.read(1)
    while(len(byte) == 1):
        yield byte[0]
        byte = stream.read(1)


def variable_bytes_iterator(stream):
    """Gives a variable number of bytes.

    Gives next byte if first bit is set."""

    it = single_byte_iterator(stream)
    first_bit = True
    while(first_bit):
        first_bit, byte = first_bit_and_rest(next(it))
        yield byte


def read_variable_length(stream):
    """Reads a variable length bytes.

    As spesified in the MIDI spesification."""
    ba = list(variable_bytes_iterator(stream))
    return sum(b << (i*7) for i, b in enumerate(reversed(ba)))
