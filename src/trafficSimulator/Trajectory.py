from LanePosition import LanePosition
import sys


class Trajectory(object):
    """
    A class that represents the trajectory of a car.
    """

    def __init__(self, car, lane, position):
        self.car = car
        self.lane = lane
        if position is None:
            position = 0
        self.current = LanePosition(self.car, lane, position)
        self.current.acquire()
        self.next = LanePosition(self.car)
        self.temp = LanePosition(self.car)
        self.isChangingLanes = False
        self.absolutePosition = None
        self.relativePosition = None

    def getLane(self):
        if self.temp.lane:
            return self.temp.lane
        else:
            return self.current.lane

    def getAbsolutePosition(self):
        if self.temp.lane is not None:
            return self.temp.position
        else:
            return self.current.position

    def getRelativePosition(self):
        return self.absolutePosition / float(self.lane.length)

    def getDirection(self):
        return self.lane.getDirection(self.relativePosition)

    def getCoords(self):
        return self.lane.getPoint(self.relativePosition)

    def nextCarDistance(self):
        if self.current.nextCarDistance().distance < self.next.nextCarDistance().distance:
            return self.current.nextCarDistance()
        else:
            return self.next.nextCarDistance()

    def distanceToStopLine(self):
        if not self.canEnterIntersection():
            return self.getDistanceToIntersection()
        return sys.maxint

    def nextIntersection(self):
        return self.current.lane.road.target

    def previousIntersection(self):
        return self.lane.road.source

    def isValidTurn(self):
        nextLane = self.car.nextLane
        sourceLane = self.current.lane
        if not nextLane:
            print "no road to enter"
            return False
        turnNumber = sourceLane.getTurnDirection(nextLane)
        if turnNumber == 3:
            print "no U-turns are allowed"
            return False
        if turnNumber == 0 and not sourceLane.isLeftmost:
            print "no left turns from this lane"
            return False
        if turnNumber == 2 and not sourceLane.isRightmost:
            print "no right turns from this lane"
            return False
        return True

    def canEnterIntersection(self):
        nextLane = self.car.nextLane
        sourceLane = self.current.lane
        if not nextLane:
            return True
        intersection = self.nextIntersection
        turnNumber = sourceLane.getTurnDirection(nextLane)
        sideId = sourceLane.road.targetSideId
        return intersection.controlSignals.state[sideId][turnNumber]

    def getDistanceToIntersection(self):
        distance = self.current.lane.length - self.car.length / 2.0 - self.current.position
        if not self.isChangingLanes:
            return max(distance, 0)
        else:
            return sys.maxint

    def timeToMakeTurn(self, plannedStep):
        if plannedStep is None:
            plannedStep = 0
        return self.getDistancetoIntersection() <= plannedStep

    def moveForward(self, distance):
        distance = max(distance, 0)
        self.current.position += distance
        self.next.position += distance
        self.temp.position += distance
        if self.timeToMakeTurn() and self.canEnterIntersection() and self.isValidTurn():
            self.startChangingLanes(self.car.popNextLane(), 0)

        if self.temp.lane:
            tempRelativePosition = float(self.temp.position) / self.temp.lane.length
        else:
            tempRelativePosition = 0
        gap = 2 * self.car.length
        if self.isChangingLanes and self.temp.position > gap and not self.current.free:
            self.current.release()

        if self.isChangingLanes and self.next.free and self.temp.position + gap > self.temp.lane.length:
            self.next.acquire()
        if self.isChangingLanes and tempRelativePosition >= 1:
            self.finishChangingLanes()
        if self.current.lane and not self.isChangingLanes and not self.car.nextLane:
            return self.car.pickNextLane()

    def changeLane(self, nextLane):
        if self.isChangingLanes:
            print "already changing lane"
            return
        if nextLane is None:
            print "no next lane"
            return
        if nextLane == self.lane:
            print "next lane == current lane"
            return
        if self.lane.road != nextLane.road:
            print "not neighbouring lanes"
            return
        nextPosition = self.current.position + 3 * self.car.length
        if nextPosition >= self.lane.length:
            print "too late to change lane"
            return
        return self.startChangingLanes(nextLane, nextPosition)

    def getIntersectionLaneChangeCurve(self):
        return

    def getAdjacentLaneChangeCurve(self):
        p1 = self.current.lane.getPoint(self.current.relativePosition)
        p2 = self.next.lane.getPoint(self.next.relativePosition)
        distance = p2.subtract(p1).length
        direction1 = self.current.lane.middleLine.vector.normalized.mult(distance * 0.3)
        control1 = p1.add(direction1)
        direction2 = self.next.lane.middleLine.vector.normalized.mult(distance * 0.3)
        control2 = p2.subtract(direction2)
        return Curve(p1, p2, control1, control2)

    def getCurve(self):
        return self.getAdjacentLaneChangeCurve()

    def startChangingLanes(self, nextLane, nextPosition):
        if self.isChangingLanes:
            print "already changing lane"
        if nextLane is None:
            print "no next lane"
        self.isChangingLanes = True
        self.next.lane = nextLane
        self.next.position = nextPosition
        curve = self.getCurve()
        self.temp.lane = curve
        self.temp.position = 0
        self.next.position -= self.temp.lane.length
        return self.next.position

    def finishChangingLanes(self):
        if not self.isChangingLanes:
            print "no lane changing is going on"
        self.isChangingLanes = False
        self.current.lane = self.next.lane
        self.current.position = self.next.position
        self.current.acquire()
        self.next.lane = None
        self.next.position = None
        self.temp.lane = None
        self.temp.position = None
        return self.current.lane

    def release(self):
        if self.current:
            self.current.release()
        if self.next:
            self.next.release()
        return self.temp.release()
