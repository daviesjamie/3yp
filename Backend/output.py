import json
import io
from structures import Operation


class JSONOutputOperation(Operation):
    """
    An operation that outputs a each object as a JSON object on a new line in the specified file.
    """
    def __init__(self, filename):
        self.output = io.open(filename, 'w', encoding='utf-8')

    def perform(self, obj):
        self.output.write(unicode(json.dumps(obj, ensure_ascii=False) + "\n"))

    def __del__(self):
        self.output.close()
