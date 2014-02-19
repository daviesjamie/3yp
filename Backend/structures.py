import abc
from collections import deque
from multiprocessing import Lock

class Operation:
    """
    Defines an operation that can be applied to items in a stream.
    """

    @abc.abstractmethod
    def perform(self, obj):
        pass


class Predicate:
    """
    Used to apply a boolean test to items in a stream, to determine if it meets some set
    criteria.
    """

    @abc.abstractmethod
    def test(self, obj):
        pass


class Function:
    """
    Applies a function to items in a stream, producing an appropriate result.
    """

    @abc.abstractmethod
    def apply(self, input):
        pass


class BufferedQueue:
    """
    Abstract implementation of a queue with a finite capacity. If the queue becomes full and
    further items are added, then those elements are dropped. In addition, if an item is
    requested from the queue and no items are present, then the system waits for an item to be
    added before returning.
    """

    @abc.abstractmethod
    def offer(self, item):
        """
        Inserts the specified element into the queue, but only if it is possible to do so
        immediately without violating capacity restrictions. Returns True if the item was added,
        and False if there is no space currently available.
        """
        pass

    @abc.abstractmethod
    def put(self, item):
        """
        Inserts the specified element into the queue. If this cannot be done without immediately
        violating capacity restrictions, then the oldest item in the queue is dropped (and
        returned) to make space for this one.
        """
        pass

    @abc.abstractmethod
    def take(self):
        """
        Retrieves and removes the head of this queue, waiting if necessary until an element
        becomes available.
        """
        pass

    @abc.abstractmethod
    def remaining_capacity(self):
        """
        Returns the number of additional elements that this queue can hold (assuming no other
        constraints).
        """
        pass


class DequeBufferedQueue(BufferedQueue):
    def __init__(self, capacity):
        self.queue = deque([], capacity)

    def offer(self, item):
        if len(self.queue) < self.queue.maxlen:
            self.queue.appendleft(item)
            return True

        return False

    def put(self, item):
        self.queue.appendleft(item)

    def take(self):
        # FIXME: This is probably a bad way of waiting for the list to be populated!
        while len(self.queue) == 0:
            pass

        return self.queue.pop()

    def remaining_capacity(self):
        return self.queue.maxlen - len(self.queue)
