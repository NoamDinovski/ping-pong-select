import select

from poller import Poller


class SelectPoller(Poller):
    """
    Poller implementation using select.select.
    """
    def __init__(self, batch_size):
        """
        Initializes a new Select-based Poller.

        :param int batch_size: The maximum amount of file descriptors to select per batch.
        """
        self.polled_sockets = []
        self.batch_size = batch_size

    def register(self, sockets):
        self.polled_sockets.extend(sockets)

    def unregister(self, sockets):
        for socket in sockets:
            self.polled_sockets.remove(socket)

    def poll_for_reading(self, timeout):
        length = len(self.polled_sockets)
        reads = []
        while length > 0:
            current_batch = self.polled_sockets[max(0, length - self.batch_size):length]
            reads_temp, _, _ = select.select(current_batch, [], [], timeout)
            reads.extend(reads_temp)
            length -= self.batch_size
        return reads

    def poll_for_writing(self, timeout):
        length = len(self.polled_sockets)
        writes = []
        while length > 0:
            current_batch = self.polled_sockets[max(0, length - self.batch_size):length]
            _, writes_temp, _ = select.select([], current_batch, [], timeout)
            writes.extend(writes_temp)
            length -= self.batch_size
        return writes
