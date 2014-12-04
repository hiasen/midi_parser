import io
import util


class FromStreamMixin:

    @classmethod
    def from_stream(cls, stream, running_status=None):
        status, = stream.read(1)
        while status == 0xf8:  # Filter out MIDI-beat clock
            status, = stream.read(1)
        return cls.from_stream_and_status(stream, status, running_status)


class BaseMidiEvent(FromStreamMixin):
    """Abstract base class for all Midi events"""

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        raise NotImplementedError("MidiEvent is an abstract class")

    def write_to(self, stream, running_status=None):
        pass

    def serialize(self):
        with io.BytesIO() as stream:
            self.write_to(stream)
            return stream.getvalue()


class SysExEvent(BaseMidiEvent):

    def __init__(self, data, status=0xf0):
        self.data = data
        self.status = status

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        data = util.read_variable_length_data(stream)
        return cls(data, status)

    def write_to(self, stream, running_status=None):
        stream.write(bytes((self.status,)))
        util.write_variable_length_data(stream, self.data)

    def __eq__(self, other):
        return self.status == other.status and self.data == other.data

    def __repr__(self):
        return "{}: data={}".format(self.__class__.__name__, self.data)

