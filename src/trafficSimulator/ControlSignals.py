from TrafficSettings import *
import random
import numpy as np
import sys


class ControlSignals(object):

    def __init__(self, intersection):
        self.intersection = intersection
        self.time = 0
        self.flipMultiplier = 1 + random.random() * 0.4 - 0.2
        self.stateNum = 0
        # TODO: make this for intersections that have more than 4 roads
        self.states = [['L', '', 'L', ''], ['FR', '', 'FR', ''], ['', 'L', '', 'L'], ['', 'FR', '', 'FR']]
        # self.states = []
        self.roads = []

    def generateState(self):
        """
        Sort the roads by their position to the center of the intersection counter-clockwise.
        Generate the states according to the roads' information.
        """
        # sort roads
        inRoads = self.intersection.getInRoads()
        quadrant1 = []
        quadrant2 = []
        quadrant3 = []
        quadrant4 = []
        for rd in inRoads:
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
        self.roads = []
        self.roads.extend(quadrant1)
        self.roads.extend(quadrant2)
        self.roads.extend(quadrant3)
        self.roads.extend(quadrant4)

        # generate states


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
        return qd, slope

    def getFlipInterval(self):
        return self.flipMultiplier * LIGHT_FLIP_INTERVAL

    def getState(self):
        if not self.states:
            self.generateState()

        if len(self.intersection.roads) <= 2:
            # TODO: make this for intersections that have more than 4 roads
            stringState = ['LFR', 'LFR', 'LFR', 'LFR']
        else:
            # stringState = self.states[self.stateNum % len(self.states)]
            stringState = self.states[self.stateNum]
        return [self.decode(x) for x in stringState]

    def decode(self, s):
        state = [0, 0, 0]
        state = [0 for _ in range(len(self.roads) - 1)]
        if s.index('L') >= 0:
            state[0] = 1
        if s.index('F') >= 0:
            state[1] = 1
        if s.index('R') >= 0:
            state[2] = 1
        return state

    def flip(self):
        if not self.states:
            self.generateState()

        # self.stateNum += 1
        self.stateNum = (self.stateNum + 1) % len(self.states)

    # def onTick(self, delta):
    #     self.time += delta
    #     if self.time > self.getFlipInterval():
    #         self.flip()
    #         self.time -= self.getFlipInterval()

