import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from QLearning import QLearning
import math
import time
from Queue import PriorityQueue
from Dijkstra import dijkstraSearch, dijkstraTrafficTime
from DispatchQL import DispatchQL
import random
from Settings import MIN_EPSILON


class Experiment(object):
    """
    The agent class that manages the whole learning process.
    """

    def __init__(self, environment, taxiNum, carNum, epsilon=0.1, alpha=0.2, gamma=0.9):
        """
        Construct an experiment object that manages all experiment process.
        :param environment: the given environment for performing experiments
        :param taxiNum: the total number of taxis
        :param carNum: the total number of cars
        :param epsilon: the exploration parameter
        :param alpha: the learning rate
        :param gamma: the discounting factor
        """
        self.env = environment
        self.taxiNum = taxiNum
        self.carNum = carNum
        self.epsilon = epsilon
        self.defaultEps = epsilon
        self.epsilonDict = {}
        self.alpha = alpha
        self.gamma = gamma

        self.taxiList = []       # contains non-called taxis
        self.calledTaxiQL = []   # contains q-learning agents for called taxis
        self.allTaxis = []       # contains all taxis

        # Q value lookup dictionary for route discovery
        # {(state, action): Q value}
        self.qvalue = {}

        # Record the visited times for state-action
        self.nsa = {}

        # Q value lookup dictionary for dispatching planning
        self.dipatchQvalue = {}
        self.dispatchNsa = {}

        # a Q-Learning model for dispatching policy
        self.dispatchQL = DispatchQL(self, self.env)

        self.iteration = 0
        self.plotMap = False
        self.goalLocation = self.env.getGoalLocation()

        self.progressCnt = 0

    def startLearning(self):
        """
        The Q learning procedure. Stop until one taxi arrives the goal location.
        At the beginning of each learning trial, perform the initialization procedure first.
        There are two Q-learning procedure: one for learning the routing policy; another for
        learning the dispatching policy.
        """
        self.initialization()
        self.iteration += 1

        while not self.env.isGoalReached():
            self.showProgress()

            interval = 0.1  # second
            self.dispatchQL.go(interval)

            if not self.env.isGoalReached():
                for car in self.env.getCars().values():
                    car.move(interval)

                # update control signals at every intersection
                self.env.updateContralSignal(interval)

        print "\narrived !!! at step: ", self.progressCnt

        self.setResetFlag(True)  # Tell animated map to wait for the initialization procedure
        self.dispatchQL.resetTrial()

    def initialization(self):
        """
        Initialize taxis, calledTaxi list and the reachGoal flag of the environment.
        """
        self.env.cleanCars()
        self.env.cleanTaxis()

        self.env.addRandomCars(self.carNum)
        self.env.addRandomTaxis(self.taxiNum)
        self.taxiList = self.env.getTaxis().values()
        self.allTaxis = self.taxiList[:]
        self.calledTaxiQL = []
        self.env.setReachGoal(False)
        self.setResetFlag(False)  # Tell the animated map to start plotting cars and taxis
        self.progressCnt = 0

    def setResetFlag(self, b):
        """
        Set the reset flag that indicates whether the learning procedure is at the
        reset step. This is for the animated map to wait for the reset procedure
        ends.
        """
        self.env.setResetFlag(b)

    def outputQvalue(self):
        if not self.plotMap:
            f = open('result/qvalue.txt', 'w')
        else:
            f = open('result/qvalue.txt', 'a')

        f.write("\n\n")
        f.write("===== No." + str(self.iteration)+" =====\n")
        for key in self.qvalue.keys():
            f.write(str(key) + ": " + str(self.qvalue[key]) + "\n")

    def outputNSA(self):
        if not self.plotMap:
            f = open('result/nsa.txt', 'w')
        else:
            f = open('result/nsa.txt', 'a')
        f.write("\n\n")
        f.write("===== No." + str(self.iteration)+" =====\n")
        for key in self.nsa.keys():
            f.write(str(key) + ": " + str(self.nsa[key]) + "\n")

    def findFastestTaxi(self):
        """
        From the goal's location, start performing search algorithm, expanding the route until reach one taxi
        and the time at other branches are longer than the found taxi.
        :return: the fastest taxi to the goal location.
        """
        goal = self.env.getGoalLocation()  # a Trajectory object
        targetInter = goal.current.lane.road.getTarget()
        sourceInter = goal.current.lane.road.getSource()
        taxi1, time1 = dijkstraSearch(self.env.realMap, sourceInter, self.allTaxis)
        taxi2, time2 = dijkstraSearch(self.env.realMap, targetInter, self.allTaxis)
        return (taxi1, time1) if time1 < time2 else (taxi2, time2)

    def callTaxi(self, taxi):
        """
        Create a QLearning object that learns the Q value of this called taxi
        :param taxi: the called taxi
        """
        goalLane = self.goalLocation.current.lane
        goalRoad = goalLane.road
        goalPosition = self.goalLocation.current.position
        taxi.beenCalled(goalRoad, goalLane, goalPosition)
        ql = QLearning(taxi, self, self.env, self.qvalue, self.nsa, self.defaultEps)
        self.calledTaxiQL.append(ql)
        self.taxiList.remove(taxi)
        print ""
        print "Called", taxi.id

    def isQuicker(self, taxi, second):
        """
        Check the time for this given taxi to the goal location is "second" quicker than other called taxis.
        :param taxi: Taxi
        :param second: int
        :return: Boolean
        """
        if not self.calledTaxiQL:
            return True

        times = []
        goalRoad = self.goalLocation.current.lane.road
        goals = [goalRoad.getTarget(), goalRoad.getSource()]
        for ql in self.calledTaxiQL:
            taxiInter = ql.taxi.trajectory.current.lane.road.getTarget()
            times.append(dijkstraTrafficTime(self.env.realMap, taxiInter, goals))
        taxiInter = taxi.trajectory.current.lane.road.getTarget()
        timeForGivenTaxi = dijkstraTrafficTime(self.env.realMap, taxiInter, goals)
        for time in times:
            if time < timeForGivenTaxi:
                return False
        return True

    def getEpsilon(self, initEps, iteration):  #TODO: create a shared function
        """
        Reduce epsilon gradually when running the learning process for many iterations
        :return: the adjusted epsilon
        """
        key = (initEps, iteration)
        if key not in self.epsilonDict:
            self.epsilonDict[key] = max(MIN_EPSILON, self.epsilon * math.pow(0.9999, iteration))
        return self.epsilonDict[key]

    def addCarTaxi(self):
        """
        Generate taxis with random initial locations
        :param taxiNum: the total number of taxis to be generated
        :return: the list of generated taxis
        """
        self.env.addRandomCars(self.carNum)
        self.env.addRandomTaxis(self.taxiNum)

    def getGoalLocation(self):
        return self.env.getGoalLocation()

    def printQValue(self):
        print "Final Q values======================================"
        for key in self.qvalue:
            print str(key) + ": " + str(self.qvalue[key]),
            if self.qvalue[key] > 0:
                print "< ================="
            else:
                print ""

    def printNSA(self):
        print "Final Nsa==========================================="
        for key in self.nsa:
            print str(key) + ": " + str(self.nsa[key])

    def showProgress(self):
        self.progressCnt += 1
        if self.progressCnt % 1000 == 0:
            print ".",
            if self.progressCnt % 50000 == 0:
                print ""
