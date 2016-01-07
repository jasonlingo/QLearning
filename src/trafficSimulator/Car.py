import random
import math
from Trajectory import Trajectory
from Traffic import *


class Car(object):
    """
    A class that represents a car.
    """

    def __init__(self, maxSpeed, lane, position):
        self.id = Traffic.uniqueId("car")
        self.speed = 0
        self.width = 0.0018   # the unit used here is km
        self.length = 0.0045
        self.distGap = 0.002
        self.maxSpeed = maxSpeed
        self.maxAcceleration = 1
        self.maxDeceleration = 3
        self.trajectory = Trajectory(self, lane, position)
        self.timeHeadway = 1.5
        self.nextLane = None
        self.alive = True
        self.preferedLane = None

    def getCoords(self):
        self.trajectory.coords

    def getSpeed(self):
        return self.speed

    def setSpeed(self, speed):
        """
        Speed should be beteen 0 ~ max speed
        :param speed: the new speed
        """
        self.speed = min(self.maxSpeed, max(speed, 0))

    def getDirection(self):
        return self.trajectory.direction

    def release(self):
        self.trajectory.release()

    def getAcceleration(self):
        """
        Get the acceleration of the speed of this car.
        :return:
        """
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
        """
        Calculate the distance of this move.
        :param delta: the given time interval
        :return:
        """
        self.speed += self.getAcceleration() * delta
        if (not self.trajectory.isChangingLanes) and self.nextLane:
            currentLane = self.trajectory.current.lane
            turnNumber = currentLane.getTurnDirection(self.nextLane)
            preferedLane = self.getPreferedLane(turnNumber, currentLane)
            if preferedLane != currentLane:
                self.trajectory.changeLane(preferedLane)

        step = self.speed * delta + 0.5 * self.getAcceleration() * math.pow(delta, 2)
        if self.trajectory.nextCarDistance.distance < step:
            print 'bad IDM'
        if self.trajectory.timeToMakeTurn(step):
            if self.nextLane is None:
                self.alive = False
        return self.trajectory.moveForward(step)

    def getPreferedLane(self, turnNumber, currentLane):
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
        laneNumber = self.getLaneNumber(turnNumber, nextRoad)
        self.nextLane = nextRoad.lanes[laneNumber]
        if not self.nextLane:
            print 'can not pick next lane'
        return self.nextLane

    def getLaneNumber(self, turnNumber, nextRoad):
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

    def __init__(self, maxSpeed, lane, position):
        super(Taxi, self).__init__(maxSpeed, lane, position)
        self.available = True
        self.destination = None
        self.source = None

    def setDestination(self, destination):
        """
        Set the destination of this trip.
        :param destination: the coordinates of the destination
        """
        self.destination = destination

    def setSource(self, source):
        """
        Set the source coordinates of this trip.
        :param source: the coordinates of the source location
        """
        self.source = source

    def getCurLocation(self):
        """
        Get the car's current coordinates and return it.
        :return:
        """

        pass

    def setRandomAvailability(self):
        """
        If the distance (here we simply use direct line distance) between the previous
        location where the availability is changed to False and the current location
        is within some certain distance, then the availability will not change.
        Otherwise, the availability will change randomly.
        :return:
        """
        if self.available or haversine(self.source, self.getCurLocation()) >= 1:  # 1 km
            if random.random() > 0.5:  #TODO: need to choose a better threshold?
                self.available = not self.available
                self.setSource(self.getCurLocation())

x


