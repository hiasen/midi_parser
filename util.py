"""Utility functions for parsing midi events and midi-files."""


# Single byte operations.

def get_nibbles(byte):
    """Returns the two nibbles of a byte."""
    return (byte & 0xf0) >> 4, byte & 0xf


def first_bit_and_rest(byte):
    """Returns the first bit and the last 7 bit of a byte"""
    return (byte & 0x80) >> 7, byte & 0x7f


# Stream operations.

def single_byte_iterator(stream):
    """Gives one byte at a time from stream."""
    try:
        while True:
            byte, = stream.read(1)
            yield byte
    except ValueError:
        pass


def variable_bytes_iterator(stream):
    """Iterates through a stream giving 7 last bit of a byte
    if the first bit of the previous byte is set."""
    for first_bit, rest in map(first_bit_and_rest,
                               single_byte_iterator(stream)):
        yield rest
        if not first_bit:
            break


def read_variable_length(stream):
    """Reads a variable length byte.

    As specified in the MIDI specification."""
    ba = list(variable_bytes_iterator(stream))
    return sum(b << (i*7) for i, b in enumerate(reversed(ba)))


# Functions for fixing running status on midi channel events

def is_real_status(status):
    """Checks if the status-message is a real status ie. not running status."""
    return 0x80 <= status < 0xf0


def has_two_params(status):
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
