import random
import math
from ControlCenter import UniqueID
from Trajectory import Trajectory


class Car:
    """
    A class that represents a car.
    """

    def __init__(self, maxSpeed, lane, position):
        self.id = UniqueID.getID()
        self.speed = 0
        self.width = 10
        self.length = 25
        self.distGap = 2
        self.maxSpeed = maxSpeed
        self.maxAcceleration = 1
        self.maxDeceleration = 3
        self.trajectory = Trajectory(self, lane, position)
        self.available = True
        self.timeHeadway = 1.5
        self.nextLane = None
        self.preferedLane = None
        self.alive = True

    def getCoords(self):
        self.trajectory.coords

    def getSpeed(self):
        return self.speed

    def setSpeed(self, speed):
        self.speed = speed

    def getDirection(self):
        return self.trajectory.direction

    def release(self):
        self.trajectory.release()

    def getAcceleration(self):
        nextCarDistance = self.trajectory.nextCarDistance()
        distanceToNextCar = max(nextCarDistance.distance, 0)
        deltaSpeed = self.speed - (nextCarDistance.car.speed if nextCarDistance is not None else 0)
        freeRoadCoeff = math.pow(self.speed / float(self.maxSpeed), 4)
        timeGap = self.speed * self.timeHeadway
        breakGap = self.speed * deltaSpeed / (2 * math.sqrt(self.maxAcceleration * self.maxDeceleration))
        safeDistance = self.distGap + timeGap + breakGap
        busyRoadCoeff = math.pow(safeDistance / float(distanceToNextCar), 2)
        safeIntersectionDist = 1 + timeGap + math.pow(self.speed, 2) / (2 * self.maxDeceleration)
        intersectionCoeff = math.pow(safeIntersectionDist / float(self.trajectory.distanceToStopLine), 2)
        coeff = 1 - freeRoadCoeff - busyRoadCoeff - intersectionCoeff
        return self.maxAcceleration * coeff

    def move(self, delta):
        self.speed += self.getAcceleration() * delta
        if (not self.trajectory.isChangingLanes) and self.nextLane:
            currentLane = self.trajectory.current.lane
            turnNumber = currentLane.getTurnDirection(self.nextLane)
            preferedLane = self.preferedLane(turnNumber, currentLane)
            if preferedLane != currentLane:
                self.trajectory.changeLane(preferedLane)
        step = self.speed * delta + 0.5 * self.getAcceleration() * math.pow(delta, 2)
        if self.trajectory.nextCarDistance.distance < step:
            print 'bad IDM'
        if self.trajectory.timeToMakeTurn(step):
            if self.nextLane is None:
                self.alive = False

        return self.trajectory.moveForward(step)

    def preferedLane(self, turnNumber, currentLane):
        if turnNumber == 0:
            return currentLane.leftmostAdjacent
        elif turnNumber == 2:
            return currentLane.rightmostAdjacent
        else:
            return currentLane

    def pickNextRoad(self):
        intersection = self.trajectory.nextIntersection
        currentLane = self.trajectory.current.lane
        possibleRoads = [road for road in intersection.roads if road.target != currentLane.road.source]
        if len(possibleRoads) == 0:
            return None

        return Traffic.sample(possibleRoads)

    def pickNextLane(self):
        if self.nextLane:
           print 'next lane is already chosen'

        self.nextLane = None
        nextRoad = self.pickNextRoad()
        if not nextRoad:
            return None
        turnNumber = self.trajectory.current.lane.road.getTurnDirection(nextRoad)
        laneNumber = self.laneNumber(turnNumber, nextRoad)
        self.nextLane = nextRoad.lanes[laneNumber]
        if not self.nextLane:
            print 'can not pick next lane'
        return self.nextLane

    def laneNumber(self, turnNumber, nextRoad):
        if turnNumber == 0:
            return nextRoad.lanesNumber - 1
        elif turnNumber == 1:
            return Traffic.rand(0, nextRoad.lanesNumber - 1)
        else:
            return 0

    def popNextLane(self):
        nextLane = self.nextLane
        self.nextLane = None
        self.preferedLane = None
        return nextLane


class Taxi(Car):
    """
    A class that represents a taxi.
    """