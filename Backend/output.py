import json
import io

from flow.structures import Operation


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


class PrintTweetOperation(Operation):
    """
    Simple operation to print the text of a tweet.
    """
    def perform(self, obj):
        print u'@{user}: {text}'.format(user=obj['user']['screen_name'], text=obj['text'])
        # print '@' + obj['user']['screen_name'] + ': ' + obj['text']


class PrintJSONOperation(Operation):
    """
    Simple operation to pretty-print JSON input. Used for testing purposes only.
    """
    def perform(self, obj):
        print json.dumps(obj, indent=4, separators=(',', ': '))
