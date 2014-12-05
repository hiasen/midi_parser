from .base import BaseMidiEvent
import util


class MetaEvent(BaseMidiEvent):
    status = 0xff

    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        event_type, = stream.read(1)
        data = util.read_variable_length_data(stream)
        return cls(event_type, data)

    def write_to(self, stream, running_status=None):
        stream.write(bytes((self.status, self.event_type)))
        util.write_variable_length_data(stream, self.data)

    def __eq__(self, other):
        return self.status == other.status and self.event_type == other.event_type and self.data == other.data

    def __repr__(self):
        return "<{}: event_type={} data={}>".format(self.__class__.__name__, self.event_type, self.data)
