import json
from stream import AbstractStream


class JSONInputStream(AbstractStream):
    """
    Loads a file containing a separate JSON object on each line into a stream for processing.
    """

    def __init__(self, filename):
        self.input = open(filename, 'r')
        self.next_line = None

    def has_next(self):
        if self.next_line is not None:
            return True

        try:
            self.next_line = self.input.next()
        except StopIteration:
            self.next_line = None

        return self.next_line is not None

    def next(self):
        if not self.has_next():
            raise Exception("Iteration has no more elements")

        to_return = json.loads(self.next_line)
        self.next_line = None

        return to_return

