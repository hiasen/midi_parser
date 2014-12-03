"""Utility functions for parsing midi events and midi-files."""


# Single byte splitting.

def get_nibbles(byte):
    """Returns the two nibbles (4 bits) of a byte."""
    return (byte & 0xf0) >> 4, byte & 0xf


def first_bit_and_rest(byte):
    """Returns the first bit and the last 7 bits of a byte"""
    return (byte & 0x80) >> 7, byte & 0x7f


# Stream operations.

def single_byte_iterator(stream):
    """Yield one byte at a time from stream."""
    try:
        while True:
            byte, = stream.read(1)
            yield byte
    except ValueError:
        pass


def variable_bytes_iterator(stream):
    """Yields the 7 last bits of each byte in a stream
    if the first bit of the previous byte is set."""
    for first_bit, rest in map(first_bit_and_rest,
                               single_byte_iterator(stream)):
        yield rest
        if not first_bit:
            break


def seven_bit_numbers_to_int(sequence):
    """Takes a sequence of 7-bit numbers and return the corresponding integer.

    Assuming a big-endian sequence.
    """
    return sum(b << (i*7) for i, b in enumerate(reversed(sequence)))


def read_variable_length_int(stream):
    """Reads a sequence of variable length bytes and gets the integer value.

    As specified in the MIDI specification."""
    return seven_bit_numbers_to_int(list(variable_bytes_iterator(stream)))


def read_variable_length_data(stream):
    """Reads variable length data from midi stream.

    First it reads the length of the data and uses that to read and return the real data.
    """
    length = read_variable_length_int(stream)
    data = stream.read(length)
    assert len(data) == length
    return data


# Functions for fixing running status on midi channel events

def is_real_status(status):
    """Checks if the status-message is a real status ie. not running status."""
    return 0x80 <= status < 0xf0


def has_two_params(status):
    """Returns true if the status type has two parameters."""
    return not 0xc0 <= status < 0xe0


def get_status_and_params(stream, status, running_status=None):
    if not is_real_status(status):
        status, *params = running_status, status
    else:
        params = stream.read(1)
    params = list(params)

    if has_two_params(status):
        params.extend(stream.read(1))
    return status, params
