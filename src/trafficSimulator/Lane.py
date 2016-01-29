import sys
from Traffic import haversine


class Lane(object):
    """
    A class that represents the lane of a road. A road might have more than one lane in one direction.
    """

    def __init__(self, road):
        """
        Construct a lane for the road
        :param road: the road that this lane belongs to
        """
        self.road = road
        self.source = road.source
        self.target = road.target
        self.leftAdjacent = None
        self.rightAdjacent = None
        self.leftmostAdjacent = None
        self.rightmostAdjacent = None
        self.length = haversine(self.source.center, self.target.center)
        # self.middleLine = None
        self.carsPosition = {}

        # self.update()

    def getSourceSideId(self):
        return self.road.sourceSideId

    def getTargetSideId(self):
        return self.road.targetSideId

    def getSideId(self):
        roads = self.road

    def getRoadId(self):
        return self.road.id

    def isRightmost(self):
        return self == self.rightmostAdjacent

    def isLeftmost(self):
        return self == self.leftmostAdjacent

    # def getLeftBorder(self):
    #     return Segment(self.sourceSegment.source, self.targetSegment.target)
    #
    # def getRightBorder(self):
    #     return Segment(self.sourceSegment.target, self.targetSegment.source)

    # def update(self):
    #     self.middleLine = Segment(self.sourceSegment.center, self.targetSegment.center)
    #     self.length = self.middleLine.length
    #     self.direction = self.middleLine.direction

    def getTurnDirection(self, other):
        return self.road.getTurnDirection(other.road)  # it now only returns 0

    def getDirection(self):
        return self.direction

    def getPoint(self, a):
        """
        return the coordinates of the position on this lane according to the relative position "a".
        :param a: the relative position from 0(source) to 1(target)
        :return: (longitude, latitude)
        """
        lng = self.source.center.lng + (self.target.center.lng - self.source.center.lng) * min(a, 1)
        lat = self.source.center.lat + (self.target.center.lat - self.source.center.lat) * min(a, 1)
        return lng, lat

    def addCarPosition(self, carPos):
        """
        Add the given carPos (LanePosition) to the self.carsPosition dictionary
        :param carPos: (LanePosition)
        """
        if carPos.id in self.carsPosition:
            print "car is already here"
        else:
            self.carsPosition[carPos.id] = carPos

    def removeCar(self, carPos):
        if carPos.id not in self.carsPosition:
            print "removing unknown car"
        del self.carsPosition[carPos.id]

    def getNext(self, carPos):
        """
        Find the car in front of the given parameter "carPos".
        :param carPos: a LanePosition of a car
        :return: the front car's LanePositions
        """
        if carPos.lane != self:
            print "car is on other lane"
            return
        next = None
        shortestDist = sys.maxint
        for car in self.carsPosition.itervalues():
            if car.position is None:
                print "the car has no position"
            distance = car.position - carPos.position
            if not car.free and (0 < distance < shortestDist):
                shortestDist = distance
                next = car
        return next

    def getCars(self):
        return [cp.car for cp in self.carsPosition.values()]
