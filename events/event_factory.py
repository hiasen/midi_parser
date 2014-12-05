from .channel_events import ChannelEvent
from .meta_events import MetaEvent
from .base import SysExEvent, FromStreamMixin


class MidiEventFactory(FromStreamMixin):

    @staticmethod
    def from_stream_and_status(stream, status, running_status=None):
        if status == 0xff:
            event_class = MetaEvent
        elif status in (0xf0, 0xf7):
            event_class = SysExEvent
        else:
            event_class = ChannelEvent
        return event_class.from_stream_and_status(stream, status, running_status)
