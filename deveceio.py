from events.event_factory import event_generator


class MidiDevice(object):

    def __init__(self,  stream):
        self.stream = stream

    def __iter__(self):
        return event_generator(self.stream)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            md = MidiDevice(f)
            for event in md:
                print(event)
