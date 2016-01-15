from Traffic import *
from Traffic import RoadType
from Lane import Lane


class Road(object):
    """
    A class that represents a road. It will connect to intersections and contain lanes.
    """

    def __init__(self, corners, center, source, target, avgSpeed=40):
        """
        Create a road that start form the source intersection to the destination intersection.
        :param corners: the four points of the road from the shapefile
        :param center: the average coordinates of this road
        :param source: the source intersection
        :param target: the target intersection
        :param avgSpeed: the average speed of this road
        """
        self.corners = corners
        self.center = center
        self.source = source
        self.target = target

        self.top, self.bottom, self.right, self.left = self.parseCorners(corners)
        self.avgSpeed = avgSpeed
        self.id = Traffic.uniqueId(RoadType.ROAD)
        # self.connectedIntersections = []
        self.lanes = []
        self.lanesNumber = None
        self.length = None
        self.setLength()
        self.targetSide = None
        self.sourceSide = None
        self.targetSideId = None
        self.sourceSideId = None
        self.update()

    def parseCorners(self, corners):
        """
        Find the top, bottom, right, and left most coordinates.
        :param corners: the given corners of this road.
        :return: the four coordinates
        """
        lats = [p.getCoords()[1] for p in corners]
        lnts = [p.getCoords()[0] for p in corners]
        maxLat = max(lats)
        minLat = min(lats)
        maxLnt = max(lnts)
        minLnt = min(lnts)
        return maxLat, minLat, maxLnt, minLnt

    def setLength(self):
        """
        Calculate the road length from the source to the target intersections.
        :return: the length of the road.
        """
        if self.source and self.target:
            self.length = haversine(self.source.center, self.target.center)

    def isConnected(self, intersection):
        """
        Check whether this road is connected to a intersection.
        :param intersection:
        :return:
        """
        for cor in intersection.corners:
            if self.bottom <= cor.getCoords()[1] <= self.top and self.left <= cor.getCoords()[0] <= self.right:
                return True
        return False

    def addIntersection(self, intersection):
        self.connectedIntersections.append(intersection)

    def leftMostLane(self):
        if self.lanes:
            return self.lanes[-1]

    def rightMostLane(self):
        if self.lanes:
            return self.lanes[0]

    def setAvgSpeed(self, speed):
        self.avgSpeed = speed

    def setSource(self, source):
        self.source = source
        self.setLength()
        self.update()

    def setTarget(self, target):
        self.target = target
        self.setLength()
        self.update()

    def getSource(self):
        return self.source

    def getTarget(self):
        return self.target

    def getLength(self):
        if self.length:
            return self.length

    def update(self):
        if not self.source or not self.target:
            # print "incomplete road"
            return

        # self.sourceSideId = self.source.rect.getSectorId(self.target.rect.center())
        # self.sourceSide = self.source.rect.getSide(self.sourceSideId).subsegment(0.5, 1.0)
        # self.targetSideId = self.target.rect.getSectorId(self.source.rect.center())
        # self.targetSide = self.target.rect.getSide(self.targetSideId).subsegment(0, 0.5)
        # self.lanesNumber = min(self.sourceSide.length, self.targetSide.length)
        # self.lanesNumber = max(2, float(self.lanesNumber) / Traffic.settings.gridSize)
        # sourceSplits = self.sourceSide.split(self.lanesNumber, True)
        # targetSplits = self.targetSide.split(self.lanesNumber)
        # if self.lanes is None or self.lanes.length < self.lanesNumber:
        #     if self.lanes is None:
        #         self.lanes = []
        #     for i in range(self.lanesNumber):
        #         if self.lanes[i] is None:
        #             self.lanes[i] = Lane(sourceSplits[i], targetSplits[i], self)
        #
        # # results = []
        # for i in range(self.lanesNumber):
        #     self.lanes[i].sourceSegment = sourceSplits[i]
        #     self.lanes[i].targetSegment = targetSplits[i]
        #     self.lanes[i].leftAdjacent = self.lanes[i + 1]
        #     self.lanes[i].rightAdjacent = self.lanes[i - 1]
        #     self.lanes[i].leftmostAdjacent = self.lanes[self.lanesNumber - 1]
        #     self.lanes[i].rightmostAdjacent = self.lanes[0]
        #     # results.append(self.lanes[i].update())
        # # return results
        self.lanes.append(Lane(self))