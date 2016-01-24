from Traffic import *
import sys


class LanePosition(object):
    """
    A class that represents the position of a car on a lane.
    """

    def __init__(self, car, lane=None, position=0):
        self.car = car
        self.lane = lane
        self.position = position
        self.id = Traffic.uniqueId("laneposition")
        self.free = True
        self.isGoalFlag = False

    def setGoal(self):
        self.isGoalFlag = True

    def isGoal(self):
        return self.isGoalFlag

    def getLane(self):
        return self.lane

    def setLane(self, lane):
        self.lane = lane

    def relativePosition(self):
        return self.position / float(self.lane.length)

    def nextCarDistance(self):
        next = self.getNext()  # this method return a LanePosition
        if next:
            rearPosition = next.position - (next.car.length / 2.0 if next.car else 0)  # the next.car might be the crash's location and will be None
            frontPosition = self.position + self.car.length / 2.0
            return next.car, rearPosition - frontPosition
        return None, sys.maxint

    def acquire(self):
        if self.lane:
            self.free = False
            self.lane.addCarPosition(self)

    def release(self):
        if not self.free and self.lane:
            self.free = True
            self.lane.removeCar(self)

    def getNext(self):
        """
        Get the front car of this current car
        :return: the front car's LanePosition
        """
        if self.lane and not self.free:
            return self.lane.getNext(self)

