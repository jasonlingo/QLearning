from TrafficSettings import *
import random
import numpy as np
import sys
import math
from Traffic import Traffic

class ControlSignals(object):

    def __init__(self, intersection):
        self.intersection = intersection
        self.time = 0
        self.id = Traffic.uniqueId("ControlSignal")
        self.flipMultiplier = 2 + random.random() * 0.4 - 0.2
        self.flipInterval = self.flipMultiplier * LIGHT_FLIP_INTERVAL
        self.stateNum = 0
        # TODO: make this for intersections that have more than 4 roads
        self.states = []
        self.inRoads = []
        self.pairNum = None  # the number of paired roads at this intersection.

    def generateState(self):
        """
        Sort the roads by their position to the center of the intersection counter-clockwise.
        Generate the states according to the roads' information.
        """
        self.states = []

        # sort roads
        tmpInRoads = self.intersection.getInRoads()
        quadrant1 = []
        quadrant2 = []
        quadrant3 = []
        quadrant4 = []
        for rd in tmpInRoads:
            qd, slope = self.getSlopeQuadrant(rd)
            if qd == 1:
                quadrant1.append((slope, rd))
            elif qd == 2:
                quadrant2.append((slope, rd))
            elif qd == 3:
                quadrant3.append((slope, rd))
            else:
                quadrant4.append((slope, rd))
        quadrant1.sort()
        quadrant2.sort()
        quadrant3.sort()
        quadrant4.sort()
        self.inRoads = []
        self.inRoads.extend(quadrant1)
        self.inRoads.extend(quadrant2)
        self.inRoads.extend(quadrant3)
        self.inRoads.extend(quadrant4)
        if len(tmpInRoads) != len(self.inRoads):
            print "number of in roads error"

        # generate states: each state can only has two roads permitted to go through the intersection
        self.pairNum = int(math.ceil(len(self.inRoads) / 2.0))
        for i in range(self.pairNum):
            l = ['' for _ in range(len(self.inRoads))]
            fr = ['' for _ in range(len(self.inRoads))]
            j = i
            while j < len(self.inRoads):
                l[j] = 'L'
                fr[j] = 'FR'
                j += self.pairNum
            self.states.append(l)
            self.states.append(fr)
        self.stateNum = random.choice([n for n in range(len(self.states))])

    def getSlopeQuadrant(self, road):
        """
        Compute the slope of the given road.
        :param road:
        :return: slope
        """
        center = np.array(self.intersection.center.getCoords())
        roadEnd = np.array(road.getSource().center.getCoords())
        diff = roadEnd - center
        if diff[0] == 0:  # vertical slope
            slope = sys.maxint if diff[1] >= 0 else -sys.maxint
        else:
            slope = diff[1] / diff[0]

        if diff[0] >= 0 and diff[1] > 0:
            qd = 1
        elif diff[0] <= 0 and diff[1] < 0:
            qd = 3
        elif diff[0] > 0 and diff[1] <= 0:
            qd = 4
        elif diff[0] < 0 and diff[1] >= 0:
            qd = 2
        else:
            print "Warn: this road is at the center of the intersection"
            qd = 1

        if diff[0] == 0 and diff[1] == 0:
            qd2 = 1
        else:
            if diff[0] > 0:
                qd2 = 1 if diff[1] > 0 else 4
            elif diff[0] == 0:
                qd2 = 1 if diff[1] > 0 else 3
            else:
                qd2 = 2 if diff[1] >= 0 else 3
        if qd != qd2:
            print "qd err!!!"

        return qd, slope

    def getTurnNumber(self, lane, isInRoad):
        """
        From the self.roads (which stores in-roads of the intersections), find the road number that the given lane belongs to.
        :param lane: the given lane to be checked
        :param isInRoad: indicates in-road (True) or out-road (False)
        :return: the order of the given lane in the self.roads
        """
        if not self.states:
            self.generateState()

        if isInRoad:
            targetPoint = lane.source.center.getCoords()
        else:
            targetPoint = lane.target.center.getCoords()

        for i in range(len(self.inRoads)):
            qd, road = self.inRoads[i]
            rdCoord = road.source.center.getCoords()
            if targetPoint == rdCoord:
                return i

        # ==== error message ====
        print "Err [ControlSignals]: Cannot find corresponding road number!"
        print "len(self.inRoads)=", len(self.inRoads)
        print "target:"
        print lane.road.target.id, lane.road.target.center.getCoords()
        print lane.road.source.id, lane.road.source.center.getCoords()
        print "roads connected to intersection", self.intersection.id, ":"
        print "In roads:"
        for road in self.intersection.getInRoads():
            print road.id, "from", road.source.center.getCoords(), "to", road.target.center.getCoords()
        print "out roads"
        for road in self.intersection.getOutRoads():
            print road.id, "from", road.source.center.getCoords(), "to", road.target.center.getCoords()

        return -1

    # def getFlipInterval(self):
    #     return self.flipMultiplier * LIGHT_FLIP_INTERVAL

    # def getState(self):
    #     if not self.states:
    #         self.generateState()
    #
    #     # if len(self.intersection.roads) <= 2:
    #     #     # TODO: make this for intersections that have more than 4 roads
    #     #     stringState = ['LFR', 'LFR', 'LFR', 'LFR']
    #     # else:
    #     #     # stringState = self.states[self.stateNum % len(self.states)]
    #     #     stringState = self.states[self.stateNum]
    #     # return [self.decode(x) for x in stringState]

    def decode(self, s):
        state = [0, 0, 0]
        state = [0 for _ in range(len(self.inRoads) - 1)]
        if s.index('L') >= 0:
            state[0] = 1
        if s.index('F') >= 0:
            state[1] = 1
        if s.index('R') >= 0:
            state[2] = 1
        return state

    def canEnterIntersection(self, sourceLane, nextLane):
        if not self.states:
            self.generateState()

        if len(self.inRoads) <= 2:
            return True
        sourceNum = self.getTurnNumber(sourceLane, True)
        nextNum = self.getTurnNumber(nextLane, False)
        permitEnter = self.states[self.stateNum][sourceNum]
        if not permitEnter:
            return False
        # endNum = (sourceNum + self.pairNum) % (2 * self.pairNum)
        # if endNum > sourceNum:
        #     RFTurn = [n for n in range(sourceNum, endNum+1)]
        # else:
        #     RFTurn = [n for n in range(sourceNum, len(self.inRoads))] + [n for n in range(endNum)]
        RFTurn = []
        for i in range(1, self.pairNum+1):
            RFTurn.append((sourceNum + i) % len(self.inRoads))
        if permitEnter == "FR":
            return nextNum in RFTurn
        else:  # 'L'
            return nextNum not in RFTurn

    def flip(self):
        # print "signal changes from", self.states[self.stateNum], "to",
        if not self.states:
            self.generateState()

        # self.stateNum += 1
        self.stateNum = (self.stateNum + 1) % len(self.states)
        # print self.states[self.stateNum]

    def updateSignal(self, delta):
        """
        :param delta: second
        :return:
        """
        self.time += delta
        if self.time > self.flipInterval:
            self.flip()
            # self.time -= self.
            self.time = 0
            return True

