import abc


class AbstractStream:
    """
    Abstract implementation of a read-only stream.
    """

    __metaclass__ = abc.ABCMeta

    def for_each(self, operation, limit=0):
        """
        Applies the given Operation to each item in the stream. The Operation executes on the
        items in the stream in the order that they appear in the stream.

        If the limit is supplied, then processing of the stream will stop after that many items
        have been processed.
        """
        if limit != 0:
            count = 0
            while self.has_next():
                operation.perform(self.next())
                count += 1
                if count >= limit:
                    break
        else:
            while self.has_next():
                operation.perform(self.next())

    def filter(self, predicate):
        """
        Transforms the stream by only keeping items that match the supplied predicate.
        """
        return FilterStream(self, predicate)

    def map(self, function):
        """
        Transforms the stream by applying the supplied function to each item in the stream,
        thus creating a new stream.
        """
        return MapStream(self, function)

    @abc.abstractmethod
    def has_next(self):
        """
        Tests to see if there are any items left in the stream to consume.
        """

    @abc.abstractmethod
    def next(self):
        """
        Fetches the next item in the stream.
        """


class FilterStream(AbstractStream):
    """
    A stream created by applying a filter (in the form of a Predicate) to another stream.
    """

    def __init__(self, source, predicate):
        self.source = source
        self.filter = predicate
        self.obj = None

    def has_next(self):
        if self.obj is not None:
            return True

        while self.source.has_next():
            self.obj = self.source.next
            if not self.filter.test(self.obj):
                self.obj = None

        return self.obj is not None

    def next(self):
        if not self.has_next():
            raise Exception("Iteration has no more elements")

        to_return = self.obj
        self.obj = None

        return to_return


class MapStream(AbstractStream):
    """
    A stream created by applying a Function to the elements in another stream.
    """

    def __init__(self, source, function):
        self.source = source
        self.function = function

    def has_next(self):
        return self.source.has_next()

    def next(self):
        return self.function.apply(self.source.next)


class Operation:
    """
    Defines an operation that can be applied to an object.
    """

    @abc.abstractmethod
    def perform(self, obj):
        pass


class Predicate:
    """
    Used to apply a boolean test to an object, to determine if it meets some set criteria.
    """

    @abc.abstractmethod
    def test(self, obj):
        pass


class Function:
    """
    Applies a function to some input, producing an appropriate result.
    """

    @abc.abstractmethod
    def apply(self, input):
        pass