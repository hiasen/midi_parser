import sys
import struct
import time
from pprint import pprint

from util import read_variable_length_int
from events import *


def parse_header(stream):
    chunk_id = stream.read(4)
    chunk_size = stream.read(4)
    format_type, number_of_tracks, time_division = struct.unpack(">HHH", stream.read(6))

    is_fpr = bool(time_division & 0x8000)
    time_division &= 0x7fff

    assert(chunk_id == b'MThd')
    assert(chunk_size == bytes([0, 0, 0, 6]))
    assert(format_type in (0, 1, 2))

    return format_type, number_of_tracks, time_division


def parse_track_header(stream):
    chunk_id = stream.read(4)
    chunk_size, = struct.unpack(">L", stream.read(4))
    assert(chunk_id == b"MTrk")
    return chunk_size


def parse_event(stream, running_status=None):
    delta_time = read_variable_length_int(stream)
    event = MidiEvent.from_stream(stream, running_status=running_status)
    return delta_time, event


def parse_file():
    stream = sys.stdin.buffer
    format_type, number_of_tracks, time_division = parse_header(stream)
    events = []
    for track_number in range(number_of_tracks):
        track_size = parse_track_header(stream)
        stop = track_size + stream.tell()

        running_status = None
        while stream.tell() < stop:
            delta_time, event = parse_event(stream, running_status)
            running_status = event.status
            events.append((delta_time, event))
    pprint(events)


def read_midi_keyboard():
    stream = sys.stdin.buffer
    running_status = None
    events = []
    while True:
        event = MidiEvent.from_stream_and_status(stream, running_status, None)
        running_status = event.status
        events.append((time.time(), event))
        print(events[-1])

if __name__ == '__main__':
    read_midi_keyboard()
    # parse_file()
