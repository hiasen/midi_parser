import io
import util


class MidiEvent(object):
    """Abstract base class for all Midi events"""
    _equality_attributes = frozenset()

    @classmethod
    def from_stream(cls, stream, running_status=None):
        status, = stream.read(1)
        while status == 0xf8:  # Filter out MIDI-beat clock
            status, = stream.read(1)
        return cls.from_stream_and_status(stream, status, running_status)

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        if status == 0xff:
            event = MetaEvent.from_stream_and_status(stream, status, None)
        elif status in (0xf0, 0xf7):
            event = SysExEvent.from_stream_and_status(stream, status, None)
        else:
            event = ChannelEvent.from_stream_and_status(stream, status, running_status)
        return event

    def __eq__(self, other):
        return all(getattr(self, attr, None) == getattr(other, attr, None)
                   for attr in self._equality_attributes)

    def write_to(self, stream):
        raise NotImplementedError("MidiEvent is an abstract class")

    def serialize(self):
        with io.BytesIO() as stream:
            self.write_to(stream)
            return stream.getvalue()


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

    def write_to(self, stream, running_status=None):
        stream.write(bytes((self.status, self.event_type)))
        util.write_variable_length_data(stream, self.data)


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

    def write_to(self, stream, running_status=None):
        stream.write(bytes((self.status, )))
        util.write_variable_length_data(stream, self.data)


class ParameterDescriptor:

    def __init__(self, index):
        self.index = index

    def __get__(self, instance, cls):
        return instance.data[self.index]

    def __set__(self, instance, value):
        instance.data[self.index] = value

    def __delete__(self, instance):
        pass


class ChannelEventRegistry(type):
    event_types = {}
    def __new__(mcs, name, bases, namespace):
        param_list = namespace.get('param_list', [])
        for i, param in enumerate(param_list):
            namespace[param] =  ParameterDescriptor(i)

        new_class = type.__new__(mcs, name, bases, namespace)
        event_type = namespace.get('event_type', None)
        if event_type is not None:
            mcs.event_types[event_type] = new_class
        return new_class


class ChannelEvent(MidiEvent, metaclass=ChannelEventRegistry):
    param_list = ('param1', 'param2')
    event_type = None

    def __init__(self, channel, data):
        self.channel = channel
        self.data = data

    @property
    def status(self):
        return (self.event_type << 4) + self.channel

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        status, params = util.get_status_and_params(stream, status, running_status)
        event_type, midi_channel = util.get_nibbles(status)
        class_to_use = ChannelEventRegistry.event_types.get(event_type, cls)
        return class_to_use(midi_channel, params)

    def __repr__(self):
        param_string = ", ".join("{}={}".format(param, self.__getattribute__(param))
                                for param in self.param_list)
        return "{}: channel={}, {}".format(self.__class__.__name__, self.channel, param_string)

    def __eq__(self, other):
        return type(self) == type(other)\
               and self.channel == other.channel\
               and all(getattr(self, param) == getattr(other, param) for param in self.param_list)

    def write_to(self, stream, running_status=None):
        if running_status != self.status:
            stream.write(bytes((self.status, )))
        stream.write(self.data)


class NoteOffEvent(ChannelEvent):
    event_type = 0x8
    param_list = ('note_number', 'velocity')


class NoteOnEvent(ChannelEvent):
    event_type = 0x9
    param_list = ('note_number', 'velocity')


class NoteAfterTouchEvent(ChannelEvent):
    event_type = 0xA
    param_list = ('note_number', 'amount')


class ControllerEvent(ChannelEvent):
    event_type = 0xB
    param_list = ('controller_type', 'value')


class ProgramChangeEvent(ChannelEvent):
    event_type = 0xC
    param_list = ('program_number',)


class ChannelAftertouchEvent(ChannelEvent):
    event_type = 0xD
    param_list = ('amount',)


class NoteAfterTouchEvent(ChannelEvent):
    event_type = 0xE
    param_list = ('value_lsb', 'value_msb')
