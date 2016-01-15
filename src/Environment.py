import random
import math
from trafficSimulator.RealMap import RealMap
from QLEnvironment import QLEnvironment
from Settings import *


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
        # Create a map
        self.realMap = realMap
        # self.map.generateSubRegion(Settings.SUB_REGION_NUM)  #TODO: add speed for each road
        # self.map.generateMapByDeletion(Settings.DELETE_ROAD_NUM)

        # Random generate a goal location
        self.realMap.setRandomGoalPosition()

        print "Goal location: coordinate=", self.goalLocation.coordinates, \
              "roadId=", self.goalLocation.roadId, \
              "intersectionId=", self.goalLocation.intersId
        self.realMap.setGoalLocation(self.goalLocation)

        # Initialize the reachGoal flag to False
        self.reachGoal = False

    # def randomLocation(self, floatNum=5):
    #     """
    #     Generate random location for taxi
    #     Args:
    #       floatNum: The number of digits to the right of the decimal point
    #     """
    #     # TODO: need change
    #     power = math.pow(10, floatNum)
    #     while True:
    #         x = random.randrange(self.right)
    #         y = random.randrange(self.top)
    #
    #         if self.map.checkRoadPoint(x, y):
    #             roadChoice = []
    #             if self.map.checkRoadPoint(x+1, y):
    #                 roadChoice.append((x+1, y))
    #             if self.map.checkRoadPoint(x-1, y):
    #                 roadChoice.append((x-1, y))
    #             if self.map.checkRoadPoint(x, y+1):
    #                 roadChoice.append((x, y+1))
    #             if self.map.checkRoadPoint(x, y-1):
    #                 roadChoice.append((x, y-1))
    #
    #             if roadChoice:
    #                 road = random.choice(roadChoice)
    #                 posX = x
    #                 posY = y
    #                 if x != road[0]:
    #                     posX = random.randrange(min(x, road[0]) * power, (max(x, road[0])) * power) / power
    #                 if y != road[1]:
    #                     posY = random.randrange(min(y, road[1]) * power, (max(y, road[1])) * power) / power
    #                 return posX, posY

    def timeToGoalState(self, fromPos):
        """
        Calculate the time from the given
        :param fromPos: the original position (x, y)
        :return: the time from the original position to the goal state's location
        """
        # TODO: need to replace this method later
        return self.realMap.trafficTime(fromPos, self.goalLocation, None)

    def getAction(self, pos):
        """
        Get the available actions for the given position.
        :param pos: (x, y) coordinates
        :return: a list of actions
        """
        return self.realMap.getAction(pos)

    def getReward(self, pos, action):
        """
        Return the Goal reward if the given position is the goal location.
        Otherwise, return the reward for non-goal position-action
        Args:
            pos: the position
            action: the action taken in the position
        Returns:
            the corresponding reward
        """
        if self.checkArriveGoal(pos):
            return Settings.GOAL_REWARD

        # TODO: modelizing
        #reward = 0.0
        # =================
        reward = -1.0 + math.pow(10, -self.realMap.trafficTime(pos, self.goalLocation, action))
        # =================
        return reward

    # def nextPos(self, taxi, action):
        # x, y = taxi.getPosition()
        #
        # subR = self.map.searchSubRegion((x, y))
        # speedMu = subR.getSpeed() if subR else 50
        #
        # speedSigmaLimit = 5.0
        #
        # speed = random.gauss(speedMu, speedSigmaLimit)
        # if speed > speedMu + speedSigmaLimit:
        #     speed = speedMu + speedSigmaLimit
        # elif speed < speedMu - speedSigmaLimit:
        #     speed = speedMu - speedSigmaLimit
        #
        # dist = speed * Settings.UNIT_TIME
        #
        # if action == Settings.EAST:
        #     x = min(x + dist, math.floor(x+1))
        #     y = self.calibrateCoordinate(y)
        # elif action == Settings.WEST:
        #     x = max(x - dist, math.ceil(x-1))
        #     y = self.calibrateCoordinate(y)
        # elif action == Settings.NORTH:
        #     y = min(y + dist, math.floor(y+1))
        #     x = self.calibrateCoordinate(x)
        # else:
        #     y = max(y - dist, math.ceil(y-1))
        #     x = self.calibrateCoordinate(x)
        #
        # return x, y

    # def calibrateCoordinate(self, num):
    #     if num >= math.ceil(num) - 0.2:
    #         num = math.ceil(num)
    #     elif num <= math.floor(num) + 0.2:
    #         num = math.floor(num)
    #     else:
    #         print "wrong coordinate: ", num
    #     return num

    def checkArriveGoal(self, pos):
        """
        Check the position is reaching the goal position. If the given position is within the goal +/- 0.2 unit distance,
        then it reaches the goal location.
        Args:
            pos: the given position
        Returns:
            True: if the position is reaching the goal location;
            False: otherwise
        """
        if abs(self.goalLocation[0] - pos[0]) < 0.2 and abs(self.goalLocation[1] - pos[1]) < 0.2:
            return True
        else:
            return False

