from abc import ABCMeta, abstractmethod


class QLInterface:
    """
    An interface/abstract class that connects the QLearning class
    and the environment.
    """
    __metaclass__ = ABCMeta

    def __init__(self, actions, bottom=0, top=50, left=0,  right=100):
        raise NotImplementedError()

    @abstractmethod
    def getReward(self):
        raise NotImplementedError()

