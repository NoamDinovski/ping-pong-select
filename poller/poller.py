import abc


class Poller(metaclass=abc.ABCMeta):
    """
    Implement this class to define a Polling Object.
    """

    @abc.abstractmethod
    def register(self, sockets):
        """
        Register the given list of sockets for polling.

        :param list sockets: The sockets to register.
        """
        pass

    @abc.abstractmethod
    def unregister(self, sockets):
        """
        Unregister the given list of sockets from polling.

        :param list sockets: The sockets to unregister.
        """
        pass

    @abc.abstractmethod
    def poll_for_reading(self, timeout):
        """
        Poll the currently registered sockets for read availability.

        :param float timeout: The timeout to poll with.
        """
        pass

    @abc.abstractmethod
    def poll_for_writing(self, timeout):
        """
        Poll the currently registered sockets for write availability.

        :param float timeout: The timeout to poll with.
        """
        pass
