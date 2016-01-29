import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from QLearning import QLearning
import math
import time
from Queue import PriorityQueue
from Dijkstra import dijkstraSearch
import random



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
        self.alpha = alpha
        self.gamma = gamma

        self.taxiList = []       # contains non-called taxis
        self.calledTaxiQL = []   # contains q-learning agents for called taxis
        self.allTaxis = []       # contains all taxis

        # Q value lookup dictionary
        # {((x, y), action): Q value}
        self.qvalue = {}

        # Record the visited times for state-action
        self.nsa = {}

        self.iteration = 0
        self.plotMap = False
        self.goalLocation = self.env.getGoalLocation()

    def startLearning(self):
        """
        The Q learning procedure. Stop until one taxi arrives the goal location.
        At the beginning of each learning trial, perform the initialization procedure first.
        There are two Q-learning procedure: one for learning the routing policy; another for
        learning the dispatching policy.
        """
        self.initialization()
        self.iteration += 1
        cnt = 0
        preTime = time.time()
        while not self.env.isGoalReached():
            cnt += 1
            if cnt % 100 == 0:
                print ".",
                if cnt % 8000 == 0: print ""

            # Call the fastest taxi in every iteration. If any non-called taxis
            # will be faster than the called taxis, the taxi will be returned.
            # Otherwise, it return None.
            # interval = min((time.time() - preTime) * 50, 100)
            # interval = min((time.time() - preTime) * 5, 200)
            # interval = random.random() * 100 + 100
            interval = (time.time() - preTime) * 1000
            print "interval", interval
            preTime = time.time()
            # interval = 100

            if not self.calledTaxiQL:
                taxi = self.findFastestTaxi()
                if taxi is not None:
                    self.callTaxi(taxi)

            # perform Q learning for called taxis
            for ql in self.calledTaxiQL:
                ql.go(interval)

            for taxi in self.taxiList:
                taxi.move(interval)
                # taxi.setRandomAvailable()

            # for taxi in self.calledTaxi:  # already put in the ql.go()
            #     taxi.move(interval * 5)

            for car in self.env.getCars().values():
                car.move(interval)  # convert millisecond to second
                # period = (time.time() - start_time)
                # print "car move uses", (time.time() - start_time), "seconds"
                # while (time.time() - start_time) * 1000 < ANIMATION_LAPSE:
                #     print ".",

            # update control signals at every intersection
            self.env.updateContralSignal(interval)


            # if cnt % 1000 == 0:
            #     for road in self.env.realMap.getRoads().values():
            #         road.updateAvgSpeed()

            # ======================================================
            # plot experiment data on map
            # ======================================================
            # self.env.map.showMap()
            # plt.plot([self.env.getGoalLocation()[0]], \
            #          [self.env.getGoalLocation()[1]], "ro")
            # for taxi in self.taxiList:
            #     plt.plot([taxi.getPosition()[0]], \
            #              [taxi.getPosition()[1]], 'bo')

            # for ql in self.calledTaxi:
            #     plt.plot([ql.getTaxi().getPosition()[0]], \
            #              [ql.getTaxi().getPosition()[1]], 'yo')
            # plt.savefig('pic/map_'+str(self.iteration)+"_"+str(cnt)+'.png')

            # print ""
            # for key in self.qvalue.keys():
            #     print key, ":", self.qvalue[key], " : ", self.nsa[key]
            #
            # if cnt % 50 == 0:
            #     raw_input("next?")

        print "\n arrived !!! at step: ", cnt

        # if (self.iteration <= 100 and self.iteration % 10 == 0) or \
        #     (self.iteration <= 1000 and self.iteration % 100 == 0) or \
        #     (self.iteration % 500 == 0):
        #     plt.clf()
        #     self.plotMap = False
        #     self.outputQvalue()
        #     self.outputNSA()
        #     self.plotResult(self.iteration)
        self.setResetFlag(True)  # Tell animated map to wait for the initialization procedure

    def initialization(self):
        """
        Initialize taxis, calledTaxi list and the reachGoal flag of the environment.
        """
        self.env.clearCars()
        self.env.clearTaxis()
        self.env.addRandomCars(self.carNum)
        self.env.addRandomTaxis(self.taxiNum)
        self.taxiList = self.env.getTaxis().values()

        self.calledTaxiQL = []

        self.env.setReachGoal(False)
        self.setResetFlag(False)  # Tell the animated map to start plotting cars and taxis


    def setResetFlag(self, b):
        """
        Set the reset flag that indicates whether the learning procedure is at the
        reset step. This is for the animated map to wait for the reset procedure
        ends.
        """
        self.env.setResetFlag(b)

    # def plotResult(self, cnt):
    #     if not self.plotMap:
    #         self.env.map.showMap()
    #         self.plotMap = True
    #
    #     # plot the route of called taxis
    #     for ql in self.calledTaxiQL:
    #         for i in range(len(ql.getTaxi().toGoalRouteX)):
    #             r = float(i) / len(ql.getTaxi().toGoalRouteX)
    #             plt.plot([ql.getTaxi().toGoalRouteX[i]], [ql.getTaxi().toGoalRouteY[i]], "o", color=(r, 0, 1))
    #         for i in range(len(ql.getTaxi().randomRouteX)):
    #             plt.plot([ql.getTaxi().randomRouteX[i]], [ql.getTaxi().randomRouteY[i]], "o", color='y')
    #
    #     # plot the route for other taxis that are not been called
    #     # for taxi in self.taxiList:
    #     #     plt.plot(taxi.randomRouteX, taxi.randomRouteY, "o", color='lightgrey')
    #
    #     plt.plot([self.env.getGoalLocation()[0]], [self.env.getGoalLocation()[1]], 'ro')
    #     plt.title("No."+str(self.iteration)+" trial")
    #     plt.savefig('result/pic/Trial_'+str(cnt)+'.png')

    def outputQvalue(self):
        if not self.plotMap:
            f = open('result/qvalue.txt', 'w')
        else:
            f = open('result/qvalue.txt', 'a')

        f.write("\n\n")
        f.write("===== No."+str(self.iteration)+" =====\n")
        for key in self.qvalue.keys():
            f.write(str(key) + ": " + str(self.qvalue[key]) +"\n")

    def outputNSA(self):
        if not self.plotMap:
            f = open('result/nsa.txt', 'w')
        else:
            f = open('result/nsa.txt', 'a')
        f.write("\n\n")
        f.write("===== No."+str(self.iteration)+" =====\n")
        for key in self.nsa.keys():
            f.write(str(key) + ": " + str(self.nsa[key]) +"\n")

    # def findFastestTaxi(self):
    #     """
    #     Find the fastest taxi to the goal location
    #     :return: the fastest taxi to the goal location
    #     """
    #     fastestTaxi = None
    #     shortestTime = sys.maxint
    #
    #     for ql in self.calledTaxiQL:
    #         time = self.env.timeToGoalState(ql.getTaxi().getPosition())
    #         if time < shortestTime:
    #             shortestTime = time
    #
    #     # Find the taxi with shorter time than the called taxis to the goal location.
    #     # By certain minutes shorter do we consider it is quicker than the called taxis to the goal location.
    #     # for taxi in self.env.getTaxis().values():
    #     #     if taxi.isAvailable():
    #     #         taxi.setAvailable(False)  # lock this taxi first
    #     #         time = self.env.timeToGoalState(taxi.getPosition())
    #     #         if time < shortestTime:
    #     #             if fastestTaxi is not None:
    #     #                 fastestTaxi.setAvailable(True)  # unlock the previous fastest taxi
    #     #             fastestTaxi = taxi
    #     #             shortestTime = time
    #     #         else:
    #     #             taxi.setAvailable(True)  # unlock this taxi
    #     return fastestTaxi

    def findFastestTaxi(self):
        """
        From the goal's location, start performing search algorithm, expanding the route until reach one taxi
        and the time at other branches are longer than the found taxi.
        :return: the fastest taxi to the goal location.
        """
        goal = self.env.getGoalLocation()  # a Trajectory object
        targetInter = goal.current.lane.road.getTarget()
        sourceInter = goal.current.lane.road.getSource()
        taxi1, time1 = dijkstraSearch(self.env.realMap, sourceInter, self.taxiList)
        taxi2, time2 = dijkstraSearch(self.env.realMap, targetInter, self.taxiList)
        return taxi1 if time1 < time2 else taxi2

    def callTaxi(self, taxi):
        """
        Create a QLearning object that learns the Q value of this called taxi
        :param taxi: the called taxi
        """
        goalLane = self.goalLocation.current.lane
        goalRoad = goalLane.road
        goalPosition = self.goalLocation.current.position
        taxi.beenCalled(goalRoad, goalLane, goalPosition)
        ql = QLearning(taxi, self.env, self.qvalue, self.nsa, self.getEpsilon())
        self.calledTaxiQL.append(ql)
        self.taxiList.remove(taxi)

        # print "call taxi no." + str(taxi.getId())

    def getEpsilon(self):
        """
        Reduce epsilon gradually when running the learning process for many iterations
        :return: the adjusted epsilon
        """
        return max(0.05, self.epsilon * math.pow(0.9999, self.iteration))

    def addCarTaxi(self):
        """
        Generate taxis with random initial locations
        :param taxiNum: the total number of taxis to be generated
        :return: the list of generated taxis
        """
        # taxis = []
        # for i in range(taxiNum):
        #     x, y = self.env.randomLocation()
        #     taxis.append(Taxi(i, x, y))
        # return taxis
        self.env.addRandomCars(self.carNum)
        self.env.addRandomTaxis(self.taxiNum)

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
