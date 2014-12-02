from util import read_variable_length, get_nibbles


class MidiEvent(object):

    @classmethod
    def from_stream(cls, stream, running_status=None):
        status, = stream.read(1)
        while(status == 0xf8):
            status, = stream.read(1)

        if status == 0xff:
            event = MetaEvent.from_stream(stream, status)
        elif status in (0xf0, 0xf7):
            event = SysExEvent.from_stream(stream, status)
        else:
            event = MidiChannelEvent.from_stream(stream,
                                                 status,
                                                 running_status)
        return event


class MetaEvent(MidiEvent):

    def __init__(self, event_type, data):
        self.type = event_type
        self.data = data

    @classmethod
    def from_stream(cls, stream, status):
        event_type, = stream.read(1)
        length = read_variable_length(stream)
        data = stream.read(length)
        obj = cls(event_type, data)
        obj.status = status
        return obj


class SysExEvent(MidiEvent):

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_stream(cls, stream, status):
        length = read_variable_length(stream)
        data = stream.read(length)
        obj = cls(data)
        obj.status = status
        return obj


class MidiChannelEvent(MidiEvent):

    def __init__(self, event_type, channel, data):
        self.event_type = event_type
        self.channel = channel
        self.data = data

    @property
    def status(self):
        return self.event_type << 4 + self.channel

    @classmethod
    def from_stream(cls, stream, status, running_status=None):
        if 0x80 <= status < 0xf0:
            param, = stream.read(1)
        else:
            param, status = status, running_status
            print("Running status")

        data = [param]

        if not 0xc0 <= status < 0xe0:
            data.extend(stream.read(1))

        event_type, midi_channel = get_nibbles(status)
        return cls(event_type, midi_channel, data)

    def __str__(self):
        return "MidiChannelEvent: {} {} {}".format(self.event_type,
                                                   self.channel,
                                                   self.data)

    __repr__ = __str__
