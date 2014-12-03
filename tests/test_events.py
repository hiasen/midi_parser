import unittest
import io

from events import MetaEvent, SysExEvent


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
        e = MetaEvent.from_stream(stream, 0xff)
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
        e = SysExEvent.from_stream(stream, 0xff)
        self.assertEqual(stream.tell(), 3)

        e2 = SysExEvent(data=bytes([0x66, 0x66]))
        self.assertEqual(e, e2)
