import unittest
import io

from events import MetaEvent, SysExEvent, ChannelEvent
from events.event_factory import MidiEventFactory


class MetaEventTest(unittest.TestCase):

    def setUp(self):
        self.event1 = MetaEvent(event_type=0x01, data=b'\x66\x66')
        self.bytes1 = b'\xff\x01\x02\x66\x66'
        self.bytestream1 = io.BytesIO(self.bytes1)

    def test_create_event(self):
        e = self.event1
        self.assertEqual(e.event_type, 0x01)
        self.assertEqual(e.data, b'\x66\x66')
        self.assertEqual(e.status, 0xff)

    def test_equal(self):
        e1 = self.event1
        e2 = MetaEvent(event_type=e1.event_type, data=e1.data)
        e3 = MetaEvent(event_type=0x22, data="hei på deg")
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test_create_from_stream(self):
        stream = self.bytestream1
        e = MetaEvent.from_stream(stream)
        self.assertEqual(stream.tell(), 5)

        e2 = self.event1
        self.assertEqual(e, e2)

    def test_serialize(self):
        my_bytes = self.event1.serialize()
        self.assertEqual(my_bytes, self.bytes1, "Serializing: {}".format(self.event1))


class SysExEventTest(unittest.TestCase):

    def setUp(self):
        self.event1 = SysExEvent(data=b'\x66\x66')
        self.bytes1 = b'\xf0\x02\x66\x66'
        self.bytestream1 = io.BytesIO(self.bytes1)

    def test_create_event(self):
        e = self.event1
        self.assertEqual(e.data, b'\x66\x66')
        self.assertEqual(e.status, 0xf0)

    def test_equal(self):
        e1 = self.event1
        e2 = SysExEvent(data=e1.data)
        e3 = SysExEvent(data=b'\x10\x10')
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test_create_from_stream(self):
        stream = self.bytestream1
        e = SysExEvent.from_stream(stream)
        self.assertEqual(stream.tell(), 4)

        e2 = self.event1
        self.assertEqual(e, e2)

    def test_serialize(self):
        my_bytes = self.event1.serialize()
        self.assertEqual(my_bytes, self.bytes1, "Serializing: {}".format(self.event1))


class MidiChannelEventTest(unittest.TestCase):

    def setUp(self):
        self.event_type = 0x8
        self.channel = 0
        self.data = b'\x66\00'
        self.event = ChannelEvent.init_subclass(
            event_type=self.event_type,
            channel=self.channel,
            params=self.data)
        self.bytes = b'\x80\x66\x00'

    def test_create_event(self):
        e = self.event
        self.assertEqual(e.event_type, self.event_type)
        self.assertEqual(e.data, self.data)
        self.assertEqual(e.channel, self.channel)

    def test_equal(self):
        e1 = self.event
        e2 = ChannelEvent.init_subclass(
            event_type=e1.event_type,
            channel=e1.channel,
            params=e1.data)
        e3 = ChannelEvent.init_subclass(
            event_type=0x9,
            channel=3,
            params=[1, 2])
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test_create_from_stream(self):
        stream = io.BytesIO(self.bytes)
        e = ChannelEvent.from_stream(stream)
        e1 = ChannelEvent.init_subclass(
            event_type=self.event_type,
            channel=self.channel,
            params=self.data)
        self.assertEqual(e, e1)


class ChannelEventRegistry(unittest.TestCase):
    pass

class MidiEventFactoryTest(unittest.TestCase):

    def test_from_stream_created_meta_event(self):
        stream = io.BytesIO(b'\xff\x01\x02\x11\x22')
        e = MidiEventFactory.from_stream(stream)
        self.assertIsInstance(e, MetaEvent)

    def test_from_stream_created_sysex_event(self):
        stream = io.BytesIO(b'\xf0\x03\x02\x11\x22')
        e = MidiEventFactory.from_stream(stream)
        self.assertIsInstance(e, SysExEvent)

    def test_from_stream_created_channel_event(self):
        stream = io.BytesIO(b'\x80\x03\x02\x11\x22')
        e = MidiEventFactory.from_stream(stream)
        self.assertIsInstance(e, ChannelEvent)
