import math
from trafficSimulator.RealMap import RealMap
from QLEnvironment import QLEnvironment


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

        self.goalLocation = self.realMap.getGoalLanePosition()
        self.reachGoal = False
        self.cars = {}
        self.taxis = {}

    def randomLocation(self):
        """
        Randomly select one land from a randomly selected road and position (0~1).
        :return: the selected lane and position.
        """
        return self.realMap.randomLaneLocation()

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
        :param pos: lane, position
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
            pos: the given position
        Returns:
            True: if the position is reaching the goal location;
            False: otherwise
        """
        if abs(self.goalLocation[0] - pos[0]) < 0.2 and abs(self.goalLocation[1] - pos[1]) < 0.2:
            return True
        else:
            return False

    def addRandomCars(self, num):
        self.realMap.addRandomCars(num)
        self.cars = self.realMap.getCars()

    def addRandomTaxis(self, num):
        self.realMap.addRandomTaxi(num)
        self.taxis = self.realMap.getTaxis()

    def clearCars(self):
        self.realMap.clearCars()
        self.cars = None

    def clearTaxis(self):
        self.realMap.clearTaxis()
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