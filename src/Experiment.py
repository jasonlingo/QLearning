import sys
from QLearning import QLearning
from Taxi import Taxi
import matplotlib.pyplot as plt
import math


class Experiment:
    """
    The agent class that manages the whole learning process.
    """

    def __init__(self, environment, taxiNum, epsilon=0.2, alpha=0.2, gamma=0.9):
        """
        Construct an experiment object that manages all experiment process.
        :param environment: the given environment for performing experiments
        :param taxiNum: the total number of taxi in the
        :param epsilon: the exploration parameter
        :param alpha: the learning rate
        :param gamma: the discounting factor
        """
        self.env = environment
        self.taxiNum = taxiNum
        self.EPSILON = epsilon
        self.ALPHA = alpha
        self.GAMMA = gamma

        self.taxiList = []
        self.calledTaxi = []
        self.allTaxis = []

        # Q value lookup dictionary
        # {((x, y), action): Q value}
        self.qvalue = {}

        # Record the visited times for state-action
        self.nsa = {}

        # for the name of plot images
        self.iteration = 0
        self.plotMap = False

    def startLearning(self):
        """
        The Q learning procedure. Stop until one taxi is arrive the goal location.
        """
        self.initialization()
        self.iteration += 1
        # print "Goal at: ", self.env.getGoalLocation()

        cnt = 0
        while not self.env.isGoalReached():
            cnt += 1
            if cnt % 500 == 0:
                print ".",
            # call the fastest taxi in every iteration
            # print "Goal location: ", self.env.getGoalLocation()
            taxi = self.findFastestTaxi()
            if taxi is not None:
                self.callTaxi(taxi)

            # perform Q learning for called taxis
            for ql in self.calledTaxi:
                ql.go()

            for taxi in self.taxiList:
                taxi.goRandomly(self.env)
                taxi.setRandomAvailable()

            # self.env.map.showMap()
            # plt.plot([self.env.getGoalLocation()[0]], \
            #          [self.env.getGoalLocation()[1]], "ro")
            # for taxi in self.taxiList:
            #     plt.plot([taxi.getPosition()[0]], \
            #              [taxi.getPosition()[1]], 'bo')
            #
            # for ql in self.calledTaxi:
            #     plt.plot([ql.getTaxi().getPosition()[0]], \
            #              [ql.getTaxi().getPosition()[1]], 'yo')
            # plt.savefig('pic/map_'+str(self.iteration)+"_"+str(cnt)+'.png')

            # print ""
            # for key in self.qvalue.keys():
            #     print key, ":", self.qvalue[key], " : ", self.nsa[key]

            # if cnt % 50 == 0:
        # raw_input("next?")

        print "\n arrived !!! at step: ", cnt

        if (self.iteration <= 100 and self.iteration % 10 == 0) or \
            (self.iteration <= 1000 and self.iteration % 100 == 0) or \
            (self.iteration % 500 == 0):
            plt.clf()
            self.plotMap = False
            self.outputQvalue()
            self.outputNSA()
            self.plotResult(self.iteration)

    def initialization(self):
        """
        Initialize taxis, calledTaxi list and the reachGoal flag of the environment.
        """
        self.taxiList = self.generateTaxi(self.taxiNum)
        for taxi in self.taxiList:
            self.allTaxis.append(taxi)
        self.calledTaxi = []
        self.env.setReachGoal(False)

    def plotResult(self, cnt):
        if not self.plotMap:
            self.env.map.showMap()
            self.plotMap = True


        # plot the route of called taxis
        for ql in self.calledTaxi:
            for i in range(len(ql.getTaxi().toGoalRouteX)):
                r = float(i) / len(ql.getTaxi().toGoalRouteX)
                plt.plot([ql.getTaxi().toGoalRouteX[i]], [ql.getTaxi().toGoalRouteY[i]], "o", color=(r, 0, 1))
            for i in range(len(ql.getTaxi().randomRouteX)):
                plt.plot([ql.getTaxi().randomRouteX[i]], [ql.getTaxi().randomRouteY[i]], "o", color='y')

        # plot the route for other taxis that are not been called
        # for taxi in self.taxiList:
        #     plt.plot(taxi.randomRouteX, taxi.randomRouteY, "o", color='lightgrey')

        plt.plot([self.env.getGoalLocation()[0]], [self.env.getGoalLocation()[1]], 'ro')
        plt.title("No."+str(self.iteration)+" trial")
        plt.savefig('result/pic/Trial_'+str(cnt)+'.png')

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

    def findFastestTaxi(self):
        """
        Find the fastest taxi to the goal location
        :return: the fastest taxi to the goal location
        """
        fastestTaxi = None
        shortestTime = sys.maxint

        # find the shortest time for the called taxis to the goal location
        # print "taxis not available=========="
        # for taxi in self.taxiList:
        #     if not taxi.isAvailable():
        #         print "Taxi no." + str(taxi.getId()) + " is not available."
        #         print "Location: ", taxi.getPosition()
        #         print ""

        # print "called taxis================="
        for ql in self.calledTaxi:
            time = self.env.timeToGoalState(ql.getTaxi().getPosition())
            # print "Taxi no." + str(ql.getTaxi().getId()) + " => " + str(time)
            # print "Location: ", ql.getTaxi().getPosition()
            # print ""
            if time < shortestTime:
                shortestTime = time

        # print "not called taxis============="
        # find the taxi with shorter time than the called taxis to the goal location
        for taxi in self.taxiList:
            if taxi.isAvailable():
                taxi.setAvailable(False)  # lock this taxi first
                time = self.env.timeToGoalState(taxi.getPosition())
                # print "Taxi no." + str(taxi.getId()) + " => " + str(time)
                # print "Location: ", taxi.getPosition()
                # print ""
                if time < shortestTime:
                    if fastestTaxi is not None:
                        fastestTaxi.setAvailable(True)  # unlock the previous fastest taxi
                    fastestTaxi = taxi
                    shortestTime = time
                else:
                    taxi.setAvailable(True)  # unlock this taxi

        return fastestTaxi

    def callTaxi(self, taxi):
        """
        Create a QLearning object that learns the Q value of this called taxi
        :param taxi: the called taxi
        """
        taxi.beenCalled()
        ql = QLearning(taxi, self.env, self.qvalue, self.nsa, self.getEpsilon())
        self.calledTaxi.append(ql)
        self.taxiList.remove(taxi)

        # print "call taxi no." + str(taxi.getId())

    def getEpsilon(self):
        return max(0.1, self.EPSILON * math.pow(0.9999, self.iteration))

    def generateTaxi(self, taxiNum):
        """
        Generate taxis with random initial locations
        :param taxiNum: the total number of taxis to be generated
        :return: the list of generated taxis
        """
        taxis = []
        for i in range(taxiNum):
            x, y = self.env.randomLocation()
            taxis.append(Taxi(i, x, y))
        return taxis

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
