from .base import BaseMidiEvent
import util


class ChannelEventParameter:

    def __init__(self, index=None, name=None):
        self.index = index
        self.name = name

    def __get__(self, instance, cls):
        return instance.data[self.index]

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError("{} has to be an integer".format(self.name))
        if not 0 <= value <= 127:
            raise ValueError("{} has to be between 0 and 127".format(self.name))
        instance.data[self.index] = value

    def __delete__(self, instance):
        pass


class ParametersMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        param_list = []
        for key, value in namespace.items():
            if isinstance(value, ChannelEventParameter) and value.index is None:
                value.index = len(param_list)
                value.name = key
                param_list.append(key)

        namespace["param_list"] = param_list
        return super().__new__(mcs, name, bases, namespace)


class EventRegisterMetaClass(type):
    event_types = {}

    def __new__(mcs, name, bases, namespace):
        new_class = super().__new__(mcs, name, bases, namespace)
        event_type = namespace.get('event_type', None)
        if event_type is not None:
            mcs.event_types[event_type] = new_class
        return new_class


class ChannelEventMetaClass(ParametersMetaClass, EventRegisterMetaClass):
    pass


class ChannelEvent(BaseMidiEvent, metaclass=ChannelEventMetaClass):
    Parameter = ChannelEventParameter

    def __init__(self, channel, data):
        self.channel = channel
        self.data = data

    @classmethod
    def instantiate_subclass(cls, event_type, channel, params):
        class_to_use = cls.event_types.get(event_type)
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
        param_string = ", ".join(
            "{}={}".format(param, self.__getattribute__(param)) for param in self.param_list)
        return "<{}: channel={}, {}>".format(self.__class__.__name__, self.channel, param_string)

    def __eq__(self, other):
        return self.status == other.status\
            and all(getattr(self, param) == getattr(other, param) for param in self.param_list)

    def write_to(self, stream, running_status=None):
        if running_status != self.status:
            stream.write(bytes((self.status, )))
        stream.write(self.data)


class NoteOffEvent(ChannelEvent):
    event_type = 0x8
    note_number = ChannelEvent.Parameter()
    velocity = ChannelEvent.Parameter()


class NoteOnEvent(ChannelEvent):
    event_type = 0x9
    note_number = ChannelEvent.Parameter()
    velocity = ChannelEvent.Parameter()


class NoteAfterTouchEvent(ChannelEvent):
    event_type = 0xA
    note_number = ChannelEvent.Parameter()
    amount = ChannelEvent.Parameter()


class ControllerEvent(ChannelEvent):
    event_type = 0xB
    controller_type = ChannelEvent.Parameter()
    value = ChannelEvent.Parameter()


class ProgramChangeEvent(ChannelEvent):
    event_type = 0xC
    program_number = ChannelEvent.Parameter()


class ChannelAftertouchEvent(ChannelEvent):
    event_type = 0xD
    amount = ChannelEvent.Parameter()


class PitchBendEvent(ChannelEvent):
    event_type = 0xE
    value_lsb = ChannelEvent.Parameter()
    value_msb = ChannelEvent.Parameter()
