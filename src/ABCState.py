from abc import ABCMeta, abstractmethod


class ABCState:
    """
    An abstract class for state.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def getState(self):
        raise NotImplementedError()

