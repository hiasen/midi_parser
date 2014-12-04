from .base import BaseMidiEvent
import util


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


class ChannelEvent(BaseMidiEvent, metaclass=ChannelEventRegistry):
    param_list = ('param1', 'param2')
    event_type = None

    def __init__(self, channel, data):
        self.channel = channel
        self.data = data

    @classmethod
    def instantiate_subclass(cls, event_type, channel, params):
        class_to_use = ChannelEventRegistry.event_types.get(event_type)
        return class_to_use(channel, params)

    @property
    def status(self):
        return (self.event_type << 4) + self.channel

    @classmethod
    def from_stream_and_status(cls, stream, status, running_status=None):
        status, params = util.get_status_and_params(stream, status, running_status)
        event_type, channel = util.get_nibbles(status)
        return cls.instantiate_subclass(event_type, channel, params)

    def __repr__(self):
        param_string = ", ".join("{}={}".format(param, self.__getattribute__(param))
                                for param in self.param_list)
        return "{}: channel={}, {}".format(self.__class__.__name__, self.channel, param_string)

    def __eq__(self, other):
        return self.status == other.status\
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


class PitchBendEvent(ChannelEvent):
    event_type = 0xE
    param_list = ('value_lsb', 'value_msb')
