import unittest
import io

from events import MetaEvent, SysExEvent, MidiChannelEvent, MidiEvent


class MetaEventTest(unittest.TestCase):

    def test_create_event(self):
        e = MetaEvent(event_type=0x01, data="hei på deg")
        self.assertEqual(e.event_type, 0x01)
        self.assertEqual(e.data, "hei på deg")
        self.assertEqual(e.status, 0xff)

    def test_equal(self):
        e1 = MetaEvent(event_type=0x01, data="hei på deg")
        e2 = MetaEvent(event_type=0x01, data="hei på deg")
        e3 = MetaEvent(event_type=0x22, data="nei på meg")
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test_create_from_stream(self):
        stream = io.BytesIO(b'\x01\x02\x66\x66\x10')
        e = MetaEvent.from_stream_and_status(stream, 0xff)
        self.assertEqual(stream.tell(), 4)

        e2 = MetaEvent(event_type=0x01, data=bytes([0x66, 0x66]))
        self.assertEqual(e, e2)


class SysExEventTest(unittest.TestCase):

    def test_create_event(self):
        e = SysExEvent(data="hei på deg", status=0xf0)
        self.assertEqual(e.data, "hei på deg")
        self.assertEqual(e.status, 0xf0)

    def test_equal(self):
        e1 = SysExEvent(data="hei på deg")
        e2 = SysExEvent(data="hei på deg")
        e3 = SysExEvent(data="nei på meg")
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test_create_from_stream(self):
        stream = io.BytesIO(b'\x02\x66\x66\x10')
        e = SysExEvent.from_stream_and_status(stream, 0xff)
        self.assertEqual(stream.tell(), 3)

        e2 = SysExEvent(data=bytes([0x66, 0x66]))
        self.assertEqual(e, e2)


class MidiChannelEventTest(unittest.TestCase):

    def test_create_event(self):
        event_type = 0x8
        channel = 0
        data = [66, 0]
        e = MidiChannelEvent(event_type=event_type, channel=channel, data=data)
        self.assertEqual(e.event_type, event_type)
        self.assertEqual(e.data, data)
        self.assertEqual(e.channel, channel)

    def test_equal(self):
        e1 = MidiChannelEvent(event_type=0x8, channel=0, data=[1, 2])
        e2 = MidiChannelEvent(event_type=0x8, channel=0, data=[1, 2])
        e3 = MidiChannelEvent(event_type=0x9, channel=3, data=[1, 2])
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test_create_from_stream(self):
        event_type = 0x8
        channel = 0
        data = [66, 0]
        stream = io.BytesIO(bytes(data))
        e = MidiChannelEvent.from_stream_and_status(stream, 0x80)
        e1 = MidiChannelEvent(event_type=event_type,
                              channel=channel,
                              data=data)
        self.assertEqual(e, e1)


class MidiEventTest(unittest.TestCase):

    def test_from_stream_created_meta_event(self):
        stream = io.BytesIO(b'\xff\x01\x02\x11\x22')
        e = MidiEvent.from_stream(stream)
        self.assertIsInstance(e, MetaEvent)

    def test_from_stream_created_sysex_event(self):
        stream = io.BytesIO(b'\xf0\x03\x02\x11\x22')
        e = MidiEvent.from_stream(stream)
        self.assertIsInstance(e, SysExEvent)

    def test_from_stream_created_channel_event(self):
        stream = io.BytesIO(b'\x80\x03\x02\x11\x22')
        e = MidiEvent.from_stream(stream)
        self.assertIsInstance(e, MidiChannelEvent)
