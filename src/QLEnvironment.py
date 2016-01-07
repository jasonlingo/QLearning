from abc import ABCMeta, abstractmethod


class QLEnvironment(object):
    """
    An abstract class that defines the required methods for interacting with Q-learning.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def randomLocation(self):
        """
        Get a random location from the map of this environment
        :return: the randomly selected location
        """
        raise NotImplementedError()

    @abstractmethod
    def timeToGoalState(self, fromPos):
        """
        Calculate the time from the given source position to the goal position
        :param fromPos: the given source position
        :return: the time (in second) for a car driving from the source position
                 to the goal position
        """
        raise NotImplementedError()

    @abstractmethod
    def getAction(self, pos):
        """
        Return legal actions for the given position
        :param pos: the given position
        :return: list of legal actions
        """
        raise NotImplementedError()

    @abstractmethod
    def getReward(self, state, action):
        """
        Get the reward for the given state and action
        :return: reward
        """
        raise NotImplementedError()

    # @abstractmethod
    # def nextPos(self):
    #     """
    #
    #     :return:
    #     """
    #     raise NotImplementedError()

    @abstractmethod
    def setReachGoal(self, newBool):
        """
        Change the status that represents whether the goal has been reached
        :param newBool: the new status
        """
        raise NotImplementedError()

    @abstractmethod
    def isGoalReached(self, loc):
        """
        Return the status of whether the goal has been reached
        :return: a boolean status
        """
        raise NotImplementedError()

    @abstractmethod
    def getGoalLocation(self):
        """
        return the goal location
        :return: the goal location
        """
        raise NotImplementedError()

    @abstractmethod
    def checkArriveGoal(self, loc):
        """
        Check the given location is reaching the goal position
        :param loc: the given location
        :return: True if the given location is reaching the goal position;
                 False otherwise
        """
        raise NotImplementedError()
