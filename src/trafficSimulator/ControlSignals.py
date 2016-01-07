from Traffic import *
from TrafficSettings import *
import random


class ControlSignals(object):

    def __init__(self, intersection):
        self.intersection = intersection
        # self.onTick = Traffic.binding(self.onTick, self) #FIXME
        self.time = 0
        self.flipMultiplier = 1 + random.random() * 0.4 - 0.2
        self.stateNum = 0
        # TODO: make this for intersections that have more than 4 roads
        self.states = [['L', '', 'L', ''], ['FR', '', 'FR', ''], ['', 'L', '', 'L'], ['', 'FR', '', 'FR']]

    def getFlipInterval(self):
        return self.flipMultiplier * LIGHT_FLIP_INTERVAL

    def getState(self):
        if len(self.intersection.roads) <= 2:
            # TODO: make this for intersections that have more than 4 roads
            stringState = ['LFR', 'LFR', 'LFR', 'LFR']
        else:
            # stringState = self.states[self.stateNum % len(self.states)]
            stringState = self.states[self.stateNum]
        return [self.decode(x) for x in stringState]

    def decode(self, s):
        # TODO: make this for intersections that have more than 4 roads
        state = [0, 0, 0]
        if s.index('L') >= 0:
            state[0] = 1
        if s.index('F') >= 0:
            state[1] = 1
        if s.index('R') >= 0:
            state[2] = 1
        return state

    def flip(self):
        # self.stateNum += 1
        self.stateNum = (self.stateNum + 1) % len(self.states)

    def onTick(self, delta):
        self.time += delta
        if self.time > self.getFlipInterval():
            self.flip()
            self.time -= self.getFlipInterval()

