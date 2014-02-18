import abc


class StreamQueue:
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