from __future__ import division
from Traffic import *
from Traffic import RoadType
from Lane import Lane
from TrafficSettings import MAX_ROAD_LANE_NUM
import numpy as np

class Road(object):
    """
    A class that represents a road. It will connect to intersections and contain lanes.
    """

    def __init__(self, corners, center, source, target, speed=40):
        """
        Create a road that start form the source intersection to the destination intersection.
        :param corners: the four points of the road from the shapefile
        :param center: the average coordinates of this road
        :param source: the source intersection
        :param target: the target intersection
        :param speed: the average speed of this road
        """
        self.corners = corners
        self.center = center
        self.source = source
        self.target = target

        self.top, self.bottom, self.right, self.left = self.parseCorners(corners)
        self.defaultSpeed = speed
        self.avgSpeed = speed
        self.recentSpeedList = [speed]
        self.id = Traffic.uniqueId(RoadType.ROAD)
        self.lanes = []
        self.lanesNumber = None
        self.length = None
        self.setLength()
        self.targetSide = None
        self.sourceSide = None
        self.targetSideId = 0 #fixme
        self.sourceSideId = 0
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

    def getCurAvgSpeed(self):
        """
        Calculate the average speed from all the cars in this road. If there is no car in this road, then return
        the default speed of this road.
        :return: the average speed (km/h)
        """
        carPosition = []
        for lane in self.lanes:
            carPosition.extend(lane.carsPosition.values())
        cars = [cp.car for cp in carPosition if cp.car is not None]
        avgSpeed = sum([car.speed for car in cars]) / len(cars) if len(cars) > 0 else self.defaultSpeed
        return avgSpeed

    def updateAvgSpeed(self):
        """
        Calculate the average speed of the recent speed data (at most 50 records) of this road.
        Then set the result to self.avgSpeed.
        """
        print "update avg speed:", self.id, self.avgSpeed, "->",
        curAvgSpeed = self.getCurAvgSpeed()
        if self.recentSpeedList >= 50:
            self.recentSpeedList.pop()
        self.recentSpeedList.append(curAvgSpeed)
        self.avgSpeed = sum(self.recentSpeedList) / len(self.recentSpeedList)
        print self.avgSpeed


    def getAvgSpeed(self):
        return max(self.avgSpeed, 1.0)

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

    # def addIntersection(self, intersection):
    #     self.connectedIntersections.append(intersection)

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
        if not self.length:
            self.setLength()
        return self.length

    def getLanes(self):
        return self.lanes

    def getTurnDirection(self, other):
        """
        Find the road of the next turn and return the corresponding road order
        :param other: the next road
        :return: the turn number
        """
        if self.target != other.source:
            print "invalid roads"
            return
        # return (other.sourceSideId - self.targetSideId - 1 + 8) % 4
        # return random.choice([x for x in range(len(other.lanes))])

        # need to determine the turn to the next road (other)
        roadOrder = []
        sourceVec = np.array(self.getSource().center.getCoords()) - np.array(self.getTarget().center.getCoords())
        for road in self.target.getOutRoads():
            targetVec = np.array(road.getTarget().center.getCoords()) - np.array(road.getSource().center.getCoords())
            angle = calcVectAngle(sourceVec, targetVec)
            if angle == 0:
                angle = 360
            roadOrder.append((angle, road))

        roadOrder.sort()
        for i, roadTup in enumerate(roadOrder):
            if roadTup[1] == other:
                return i

    def update(self):
        if not self.source or not self.target:
            return
        # ToDo: check
        # self.sourceSideId = self.source.rect.getSectorId(self.target.rect.center())
        # self.sourceSide = self.source.rect.getSide(self.sourceSideId).subsegment(0.5, 1.0)
        # self.targetSideId = self.target.rect.getSectorId(self.source.rect.center())
        # self.targetSide = self.target.rect.getSide(self.targetSideId).subsegment(0, 0.5)
        # self.lanesNumber = min(self.sourceSide.length, self.targetSide.length)
        # self.lanesNumber = max(2, float(self.lanesNumber) / Traffic.settings.gridSize)
        # sourceSplits = self.sourceSide.split(self.lanesNumber, True)
        # targetSplits = self.targetSide.split(self.lanesNumber)
        # if self.lanes is None or len(self.lanes) < self.lanesNumber:
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
            # results.append(self.lanes[i].update())
        # return results

        # if not self.lanes:
        #     self.lanes.append(Lane(self))
        while len(self.lanes) < MAX_ROAD_LANE_NUM:
            self.lanes.append(Lane(self))
