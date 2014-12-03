import util


class MidiEvent(object):
    _equality_attributes = frozenset()

    @classmethod
    def from_stream(cls, stream, running_status=None):
        status, = stream.read(1)
        while(status == 0xf8):  # Filter out MIDI-beat clock
            status, = stream.read(1)
        return cls.from_stream_and_status(stream, status, running_status)

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        if status == 0xff:
            event = MetaEvent.from_stream_and_status(stream, status, None)
        elif status in (0xf0, 0xf7):
            event = SysExEvent.from_stream_and_status(stream, status, None)
        else:
            event = MidiChannelEvent.from_stream_and_status(stream, status, running_status)
        return event


    def __eq__(self, other):
        return all(getattr(self, attr, None) == getattr(other, attr, None)
                   for attr in self._equality_attributes)


class MetaEvent(MidiEvent):
    _equality_attributes = frozenset(('event_type', 'data'))

    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
        self.status = 0xff

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        event_type, = stream.read(1)
        data = util.read_variable_length_data(stream)
        obj = cls(event_type, data)
        obj.status = status
        return obj


class SysExEvent(MidiEvent):
    _equality_attributes = frozenset(('data',))

    def __init__(self, data, status=0xf0):
        self.data = data
        self.status = status

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        data = util.read_variable_length_data(stream)
        obj = cls(data)
        obj.status = status
        return obj


class MidiChannelEvent(MidiEvent):
    _equality_attributes = frozenset(('event_type', 'data', 'channel'))

    def __init__(self, event_type, channel, data):
        self.event_type = event_type
        self.channel = channel
        self.data = data

    @property
    def status(self):
        return (self.event_type << 4) + self.channel

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        status, params = util.get_status_and_params(stream, status, running_status)
        event_type, midi_channel = util.get_nibbles(status)
        return cls(event_type, midi_channel, params)

    def __str__(self):
        return "MidiChannelEvent: {} {} {}".format(self.event_type,
                                                   self.channel,
                                                   self.data)

    __repr__ = __str__
