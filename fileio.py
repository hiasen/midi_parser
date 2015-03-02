from events.event_factory import MidiEventFactory, event_generator
import util
import struct


def delta_time_event_generator(stream, bytes_to_read):
    stop = stream.stell() + bytes_to_read
    event_iterator = event_generator(stream)
    while stream.tell() < stop:
        delta_time = util.read_variable_length_int(stream)
        event = next(event_iterator)
        yield delta_time, event


class ChunkParserMixin:
    _CHUNK_ID = None

    @classmethod
    def get_entire_chunk(cls, stream):
        chunk_size = cls.get_chunk_size(stream)
        return stream.read(chunk_size)

    @classmethod
    def get_chunk_size(cls, stream):
        chunk_id = stream.read(4)
        cls._assert_correct_chunk_id(chunk_id)
        chunk_size, = struct.unpack(">L", stream.read(4))
        return chunk_size

    @classmethod
    def _assert_correct_chunk_id(cls, chunk_id):
        if chunk_id != cls._CHUNK_ID:
            raise ValueError('Wrong chunk id in header. Got {} expected {}'.format(
                chunk_id, cls._CHUNK_ID))


class MidiTrack(ChunkParserMixin, object):
    _CHUNK_ID = b'MTrk'

    def __init__(self, events=None):
        self.events = events

    @classmethod
    def from_stream(cls, stream):
        chunk_size = cls.get_chunk_size(stream)
        events = list(delta_time_event_generator(stream, chunk_size))
        return cls(events=events)

    def __str__(self):
        string = [self.__class__.__name__, "Number of events:{}".format(len(self.events))]
        string.extend("time: {} \t{}".format(t, e) for t, e in self.events)
        return "\n".join(string)


class MidiFile(ChunkParserMixin, object):
    _CHUNK_ID = b'MThd'

    def __init__(self, format_type, time_division):
        self.format_type = format_type
        self.time_division = time_division
        self.tracks = []

    @classmethod
    def from_stream(cls, stream):
        format_type, number_of_tracks, time_division = MidiFile.parse_header(stream)
        obj = MidiFile(format_type, time_division)
        obj.tracks = [MidiTrack.from_stream(stream) for _ in range(number_of_tracks)]
        return obj

    @classmethod
    def from_filename(cls, filename):
        with open(filename, "rb") as stream:
            return cls.from_stream(stream)

    @classmethod
    def parse_header(cls, stream):
        """Returns the a tuple of the form (format_type, number_of_tracks, time_division)"""
        header_bytes = cls.get_entire_chunk(stream)
        return struct.unpack(">HHH", header_bytes[:6])

    def __str__(self):
        str_lst = [self.__class__.__name__,
                   "format_type: {}".format(self.format_type),
                   "number_of_tracks: {}".format(len(self.tracks)),
                   "time_division: {}".format(self.time_division),
                   ]
        track_string = "\n".join("Track{}: {}".format(i, track)
                                 for i, track in enumerate(self.tracks))
        str_lst.append(track_string)
        return "\n".join(str_lst)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            midi_file = MidiFile.from_stream(f)
        print(midi_file)
