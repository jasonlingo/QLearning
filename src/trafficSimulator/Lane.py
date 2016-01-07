import sys


class Lane(object):
    """
    A class that represents the lane of a road. A road might have more than one lane in one direction.
    """

    def __init__(self, sourceSegment, targetSegment, road):
        self.sourceSegment = sourceSegment
        self.targetSegment = targetSegment
        self.road = road
        self.leftAdjacent = None
        self.rightAdjacent = None
        self.leftmostAdjacent = None
        self.rightmostAdjacent = None
        self.carsPosition = {}
        self.update()
        self.length = None
        self.middleLine = None

    def getSourceSideId(self):
        return self.road.sourceSideId

    def getTargetSideId(self):
        return self.road.targetSideId

    def isRightmost(self):
        return self == self.rightmostAdjacent

    def isLeftmost(self):
        return self == self.leftmostAdjacent

    def getLeftBorder(self):
        return Segment(self.sourceSegment.source, self.targetSegment.target)

    def getRightBorder(self):
        return Segment(self.sourceSegment.target, self.targetSegment.source)

    def update(self):
        self.middleLine = Segment(self.sourceSegment.center, self.targetSegment.center)
        self.length = self.middleLine.length
        self.direction = self.middleLine.direction

    def getTurnDirection(self, other):
        return self.road.getTurnDirection(other.road)

    def getDirection(self):
        return self.direction

    def getPoint(self, a):
        return self.middleLine.getPoint(a)

    def addCarPosition(self, carPos):
        if carPos.id in self.carsPosition:
            print "car is already here"
        self.carsPosition[carPos.id] = carPos

    def removeCar(self, carPos):
        if carPos.id not in self.carsPosition:
            print "removing unknown car"
        del self.carsPosition[carPos.id]

    def getNext(self, carPos):
        if carPos.lane != self:
            print "car is on other lane"
        next = None
        bestDistance = sys.maxint
        for car in self.carsPosition.itervalues():
            distance = car.position - carPos.position
            if not car.free and (0 < distance < bestDistance):
                bestDistance = distance
                next = car
        return next

