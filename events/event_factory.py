from .channel_events import ChannelEvent
from .meta_events import MetaEvent
from .base import SysExEvent, FromStreamMixin


class MidiEventFactory(FromStreamMixin):

    @staticmethod
    def from_stream_and_status(stream, status, running_status=None):
        if status == 0xff:
            return MetaEvent.from_stream_and_status(stream, status, None)
        elif status in (0xf0, 0xf7):
            return SysExEvent.from_stream_and_status(stream, status, None)
        else:
            return ChannelEvent.from_stream_and_status(stream, status, running_status)
