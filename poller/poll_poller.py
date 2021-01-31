import select

from poller import Poller


class PollPoller(Poller):
    """
    Poller implementation using select.poll objects.
    """
    def __init__(self):
        self.poll_object = select.poll()
        self.socket_to_descriptor = {}

    def register(self, sockets):
        for socket in sockets:
            self.poll_object.register(socket, select.POLLIN | select.POLLPRI | select.POLLOUT)
            self.socket_to_descriptor[socket.fileno()] = socket

    def unregister(self, sockets):
        for socket in sockets:
            self.poll_object.unregister(socket)
            self.socket_to_descriptor.pop(socket.fileno())

    def poll(self, timeout, event_mask):
        """
        Polls the poll object and returns the sockets that support
        the events defined by the given event mask.

        :param float timeout: The timeout to poll with.
        :param int event_mask: The bitmask of polling events to filter by.
        :return:
        """
        return [self.socket_to_descriptor[fd] for fd, event_type in self.poll_object.poll(timeout)
                if event_type & event_mask != 0]

    def poll_for_reading(self, timeout):
        return self.poll(timeout, select.POLLIN | select.POLLPRI)

    def poll_for_writing(self, timeout):
        return self.poll(timeout, select.POLLOUT)
