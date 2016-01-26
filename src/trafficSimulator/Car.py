import math
from Trajectory import Trajectory
from Traffic import *
from TrafficSettings import *


class Car(object):
    """
    A class that represents a car.
    """

    def __init__(self, lane, position=0, maxSpeed=MAX_SPEED, carType="Car"):
        """
        :param lane:
        :param position: the relative position of this car in the given lane
        :param maxSpeed: km/h
        :return:
        """
        self.id = Traffic.uniqueId(carType)
        self.speed = 0
        self.width = 0.0018     # the unit used here is km
        self.length = 0.0045    # the length (km) of this car
        self.maxSpeed = maxSpeed
        self.trajectory = Trajectory(self, lane, position)
        self.nextLane = None
        self.alive = True
        self.preferedLane = None

    def getCoords(self):
        """
        Return the coordinates of this car.
        :return: (lat, lng), lat and lng represents the latitude and longitude respectively
        """
        return self.trajectory.getCoords()

    def getSpeed(self):
        """
        :return: the speed (km/h)
        """
        return self.speed

    def setSpeed(self, speed):
        """
        Set the current speed of this car to the given speed parameter.
        The speed should be between 0 ~ max.
        :param speed: the new speed
        """
        self.speed = min(self.maxSpeed, max(round(speed, 10), 0))

    def getDirection(self):
        """
        Get the current direction of this car.
        :return:
        """
        return self.trajectory.direction

    def release(self):
        self.trajectory.release()

    def getAcceleration(self):
        """
        Get the acceleration of the speed of this car.
        For the detail of this model, refer to https://en.wikipedia.org/wiki/Intelligent_driver_model
        :return: accelerating speed
        """
        timeHeadway = 1.5        # second
        distGap = 0.002          # km
        maxAcceleration = 0.001  # the maximum acceleration (km/s^2)
        maxDeceleration = 0.003  # the maximum deceleration (km/s^2)

        nextCar, nextDistance = self.trajectory.nextCarDistance()
        distanceToNextCar = max(nextDistance, 0)
        deltaSpeed = self.speed - (nextCar.speed if nextCar is not None else 0)
        speedRatio = (self.speed / self.maxSpeed)
        freeRoadCoeff = pow(speedRatio, 4)  # TODO: make maxSpeed follow Gaussian distribution

        timeGap = self.speed * timeHeadway / 3600.0  # (km/h) * (second/3600)
        breakGap = self.speed * deltaSpeed / (2 * math.sqrt(maxAcceleration * maxDeceleration))
        safeDistance = distGap + timeGap + breakGap
        distRatio = (safeDistance / float(distanceToNextCar if distanceToNextCar > 0 else 0.00001))  # FIXME: divide by zero
        busyRoadCoeff = pow(distRatio, 2)

        safeIntersectionDist = 0.001 + timeGap + pow(self.speed, 2) / (2 * maxDeceleration)  # check unit
        safeInterDistRatio = (safeIntersectionDist / float(self.trajectory.distanceToStopLine() if self.trajectory.distanceToStopLine() > 0 else 0.00001))
        intersectionCoeff = pow(safeInterDistRatio, 2)

        coeff = 1 - freeRoadCoeff - busyRoadCoeff - intersectionCoeff
        # return round(max(min(maxAcceleration * coeff, maxAcceleration), -maxDeceleration), 10)
        return round(maxAcceleration * coeff, 10)

    def move(self, second):
        """
        Calculate the distance of this move by the given time and speed of the car.
        Check whether the car can go the computed distance without hitting front car
        or arriving the intersection.
        If the car is going to arrive at a intersection, check the traffic light and choose
        to go straight, turn right, or left.
        :param second: the given time interval in second
        """
        # print "car move"
        acceleration = self.getAcceleration()
        # print "car:", self.id, " acc:", acceleration,
        # self.speed += acceleration * second * 3600  # convert km/s to km/h
        # print "speed=", self.speed, "->",
        self.setSpeed(self.speed + acceleration * second * 3600)
        # print self.speed

        # if (not self.trajectory.isChangingLanes) and self.nextLane:
        #     currentLane = self.trajectory.current.lane
        #     turnNumber = currentLane.getTurnDirection(self.nextLane)  # FIXME: it now only returns 0
        #     preferedLane = self.getPreferedLane(turnNumber, currentLane)
        #     if preferedLane != currentLane:  #FIXME: it only returns the currentLane
        #         self.trajectory.changeLane(preferedLane)

        step = self.speed * second / 3600.0 + 0.5 * acceleration * math.pow(second, 2)
        nextCarDist = self.trajectory.nextCarDistance()[1]
        if nextCarDist < step:
            # print 'step is longer than the distance to the next car'
            step = nextCarDist
        if self.trajectory.timeToMakeTurn(step):
            if self.nextLane is None:
                # self.alive = False  #FIXME: if there is no nextLane chosen yet, pick one
                self.pickNextLane()
        self.trajectory.moveForward(step)

    def getPreferedLane(self, turnNumber, currentLane):
        # if turnNumber == 0:
        #     return currentLane.leftmostAdjacent
        # elif turnNumber == 2:
        #     return currentLane.rightmostAdjacent
        # else:
        #     return currentLane
        return currentLane

    def pickNextRoad(self):
        """
        Randomly pick the next road from the outbound roads of the target intersection.
        The car cannot make a U-turn unless there is no other road.
        :return: a randomly picked road.
        """
        intersection = self.trajectory.nextIntersection()
        currentLane = self.trajectory.current.lane
        possibleRoads = [road for road in intersection.roads if road.target != currentLane.road.source]
        if not possibleRoads:
            possibleRoads = [road for road in intersection.getRoads()]
            if not possibleRoads:
                print "Err: There is no road to pick"
                return None
        return sample(possibleRoads, 1)[0]

    def pickNextLane(self):
        if self.nextLane:
            print 'next lane is already chosen'
            #return  # FIXME

        self.nextLane = None
        nextRoad = self.pickNextRoad()
        if not nextRoad:
            return None
        turnNumber = self.trajectory.current.lane.road.getTurnDirection(nextRoad)
        # laneNumber = self.getLaneNumber(turnNumber, nextRoad)
        # print "laneNumber:", laneNumber, len(nextRoad.lanes)
        self.nextLane = nextRoad.lanes[turnNumber] if turnNumber < len(nextRoad.lanes) else None
        if not self.nextLane:
            print 'cannot pick next lane'
        # print "nextLane", self.nextLane
        # return self.nextLane

    def getLaneNumber(self, turnNumber, nextRoad): #FIXME
        # if turnNumber == 0:
        #     return nextRoad.lanesNumber - 1
        # elif turnNumber == 1:
        #     return rand(0, nextRoad.lanesNumber - 1)
        # else:
        #     return 0
        return 0  # now there is only one lane in each road

    def popNextLane(self):
        nextLane = self.nextLane
        self.nextLane = None
        self.preferedLane = None
        return nextLane

    def getCurLocation(self):
        """
        Get the car's current coordinates and return it.
        :return:
        """
        pass


class Taxi(Car):
    """
    A class that represents a taxi.
    """

    def __init__(self, lane, position, maxSpeed=MAX_SPEED, carType="Taxi"):
        super(Taxi, self).__init__(lane, position, maxSpeed, carType)
        self.available = True
        self.destRoad = None
        self.destLane = None
        self.destPosition = None
        self.called = False
        # self.source = None

    def setDestination(self, destination):
        """
        Set the destination of this trip.
        :param destination: the coordinates of the destination
        """
        self.destination = destination

    # def setSource(self, source):
    #     """
    #     Set the source coordinates of this trip.
    #     :param source: the coordinates of the source location
    #     """
    #     self.source = source

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

    def setAvailable(self, avail):
        self.available = avail

    def isAvailable(self):
        return self.available

    def call(self, road, lane, position):
        if not self.available:
            return False
        self.setAvailable(False)
        self.called = True
        self.destRoad = road
        self.destLane = lane
        self.destPosition = position


