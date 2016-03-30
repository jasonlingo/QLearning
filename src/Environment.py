import math
from trafficSimulator.RealMap import RealMap
from QLEnvironment import QLEnvironment
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Settings import *
from trafficSimulator.TrafficSettings import CLOSE_CRASH_LANE, CLOSE_CRASH_LANE_ALL
from trafficSimulator.Car import Car


class Environment(QLEnvironment):
    """
    An Environment class that inherits from the QLInterface.
    It implements all the methods for QLearning class's needs.
    """

    def __init__(self, realMap):
        """
        :param realMap (RealMap): the map for this environment
        :return:
        """
        self.realMap = realMap

        # TODO: add speed for each road
        # self.map.generateSubRegion(Settings.SUB_REGION_NUM)
        # self.map.generateMapByDeletion(Settings.DELETE_ROAD_NUM)

        # print "Goal location: coordinate=", self.goalLocation.coordinates, \
        #       "roadId=", self.goalLocation.roadId, \
        #       "intersectionId=", self.goalLocation.intersId

        self.goalLocation = self.realMap.getGoalLanePosition()  # Trajectory object
        self.block = None
        if CLOSE_CRASH_LANE:
            self.block = self.closeLane(self.goalLocation.current.lane)
        self.reachGoal = False
        self.cars = {}
        self.taxis = {}

    def randomLocation(self):
        """
        Randomly select one land from a randomly selected road and position (0~1).
        :return: the selected lane and position.
        """
        return self.realMap.randomLaneLocation()

    def closeLane(self, lane):
        """
        Put one Car object at the begin of the lane as a block.
        :param lane: the given lane to be blocked
        :return: a list of block object
        """
        if CLOSE_CRASH_LANE_ALL:
            block = []
            for l in lane.road.getLanes():
                block.append(Car(l))
            return block
        return [Car(lane)]

    def timeToGoalState(self, fromPos):
        """
        Calculate the time from the given position to the goal position
        :param fromPos: the original position (x, y)
        :return: the time from the original position to the goal state's location
        """
        # TODO: need to replace this method later
        return self.realMap.trafficTime(fromPos, self.goalLocation, None)

    def getAction(self, pos):
        """
        Get the available actions for the given position.
        :param pos: LanePosition
        :return: a list of actions
        """
        return self.realMap.getAction(pos)

    def getReward(self, pos, action):
        """
        Return the Goal reward if the given position is the goal location.
        Otherwise, return the reward for non-goal position-action
        Args:
            pos: Road
            action: Road
        Returns:
            the corresponding reward
        """
        if self.checkArriveGoal(pos):
            return GOAL_REWARD

        #reward = 0.0
        # =================
        reward = -1.0 + math.pow(10, -self.realMap.trafficTime(pos, self.goalLocation.current.lane.road) / 100.0)
        # =================
        return reward

    def setReachGoal(self, newBool):
        self.reachGoal = newBool

    def isGoalReached(self):
        return self.reachGoal

    def getGoalLocation(self):
        """
        :return: a Trajectory object containing the lane and position of the goal location
        """
        return self.goalLocation

    def checkArriveGoal(self, pos):
        """
        Check whether the position reaches the goal position. If the given position is
        within the goal +/- 0.2 unit distance, then it reaches the goal location.
        Args:
            pos: Road
        Returns:
            True: if the position is reaching the goal location;
            False: otherwise
        """
        goalRoad = self.goalLocation.current.lane.road
        goalInters = [goalRoad.getTarget(), goalRoad.getSource()]  # two intersections connecting to this road
        if pos.getTarget() in goalInters:
            return True
        if pos.getSource() in goalInters:
            return True
        return False

    def addRandomCars(self, num):
        self.realMap.addRandomCars(num)
        self.cars = self.realMap.getCars()

    def addRandomTaxis(self, num):
        self.realMap.addRandomTaxi(num)
        self.taxis = self.realMap.getTaxis()

    def cleanCars(self):
        self.realMap.cleanCars()
        self.cars = None

    def cleanTaxis(self):
        self.realMap.cleanTaxis()
        self.taxis = None

    def getCars(self):
        return self.cars

    def getTaxis(self):
        return self.taxis

    def setResetFlag(self, b):
        self.realMap.setResetFlag(b)

    def changeContralSignal(self, delta):
        self.realMap.changeContralSignal(delta)

    def setCarRunsOK(self, b):
        self.realMap.setCarRunsOK(b)

    def isAniMapPlotOk(self):
        return self.realMap.isAniMapPlotOk()

    def updateContralSignal(self, delta):
        self.realMap.updateContralSignal(delta)