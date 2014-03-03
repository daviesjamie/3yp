from structures import Operation


class NullOperation(Operation):
    """
    An empty operation that does nothing, it is simply used to pull objects through the stream.
    Used for testing purposes only.
    """
    def perform(self, obj):
        pass


class PrintOperation(Operation):
    """
    Simple operation to print whatever input is supplied. Used for testing purposes only.
    """
    def perform(self, obj):
        print obj


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
