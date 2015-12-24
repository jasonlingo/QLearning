from Traffic import *


class Road:
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
        self.top, self.bottom, self.right, self.left = self.parseCorners(corners)
        self.source = source
        self.target = target
        self.avgSpeed = avgSpeed
        self.id = Traffic.uniqueID(RoadType.ROAD)
        self.connectedIntersections = []
        self.lanes = []
        self.lanesNumber = None
        self.length = None
        self.setLength()

    def parseCorners(self, corners):
        """
        Find the top, bottom, right, and left most coordinates.
        :param corners: the given corners of this road.
        :return: the four coordinates
        """
        lats = [p[0] for p in corners]
        lnts = [p[1] for p in corners]
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
            if self.bottom <= cor[0] <= self.top and self.left <= cor[1] <= self.right:
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

    def setTarget(self, target):
        self.target = target
        self.setLength()

    def getSource(self):
        return self.source

    def getTarget(self):
        return self.target

    def getLength(self):
        if self.length:
            return self.length