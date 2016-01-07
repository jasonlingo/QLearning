import shapefile as shp
import pygmaps
import webbrowser
import os
from Traffic import RoadType
from Road import Road
from Intersection import Intersection


class Shapefile(object):
    """
    A class that load road data from a shapefile and output as desired data structure.
    """

    def __init__(self, filename):
        """
        :param filename: the filename of a shapefile
        """
        self.ctr = shp.Reader(filename)
        self.shapeRecords = self.ctr.iterShapeRecords()

        self.roads = {}
        self.intersections = {}

    def getRoads(self):
        """
        Read the shapefile and get all the coordinates of roads.
        :return:
        """
        if not self.roads:
            self.roads = self.readData(RoadType.ROAD)
        return self.roads

    def getIntersections(self):
        """
        Read the shapefile and get all the coordinates of intersections.
        :return: a list of intersection data
        """
        if not self.intersections:
            self.intersections = self.readData(RoadType.INTERSECTION)
        return self.intersections

    def readData(self, roadType):
        """
        Get the data out according to given road type. The road types include
        'Median Hidden', 'Median Island', 'Parking Garage', 'Road Hidden', 'Alley',
        'Paved Drive', 'Hidden Median', 'Parking Lot', 'trafficSimulator Island', 'Intersection',
        'Road'. The output coordinate will be the center (average of the coordinates)
        of the road type.

        :param roadType: the given road type.
        :return: a list of coordinates for the road type.
        """
        data = []
        check = []
        objs = []
        for sh in self.ctr.iterShapeRecords():
            if sh.record[3] == roadType:
                lats = [p[1] for p in sh.shape.points]
                lnts = [p[0] for p in sh.shape.points]
                centerLats = sum(lats) / float(len(lats)) if len(lats) > 0 else None
                centerLnts = sum(lnts) / float(len(lnts)) if len(lnts) > 0 else None
                center = (centerLats, centerLnts)
                if centerLats and centerLnts:
                    data.append(center)

                maxLat, minLat = max(lats), min(lats)
                maxLnt, minLnt = max(lnts), min(lnts)
                corners = [tuple([(p[1], p[0]) for p in sh.shape.points if p[1] == maxLat][0])]
                corners.append(tuple([(p[1], p[0]) for p in sh.shape.points if p[1] == minLat][0]))
                corners.append(tuple([(p[1], p[0]) for p in sh.shape.points if p[0] == maxLnt][0]))
                corners.append(tuple([(p[1], p[0]) for p in sh.shape.points if p[0] == minLnt][0]))
                check.extend(corners)
                objs.append(self.makeRoads(roadType, corners, center))

        # return data, check
        return objs

    def makeRoads(self, roadType, corners, center):
        """
        Create a road or intersection according to the given road type.
        :return: a created road or intersection
        """
        if roadType == RoadType.ROAD:
            return Road(corners, center, None, None)
        elif roadType == RoadType.INTERSECTION:
            return Intersection(corners, center, None) # FIXME, rect

    def plotMap(self, intersections, roads, interCheck, roadCheck):
        print "Total points:", len(intersections) + len(roads)
        if not intersections and not roads:
            print "not points to plot"
            return

        mymap = pygmaps.maps(intersections[0][0], intersections[0][1], 12)

        for point in roads:
            mymap.addpoint(point[0], point[1], "#00FF00")
        for point in intersections:
            mymap.addpoint(point[0], point[1], "#0000FF")
        for point in interCheck:
            mymap.addpoint(point[0], point[1], "#00FFFF")
        for point in roadCheck:
            mymap.addpoint(point[0], point[1], "#FFFF00")

        mapFilename = "shapefileMap.html"
        mymap.draw('./' + mapFilename)

        # Open the map file on a web browser.
        url = "file://" + os.getcwd() + "/" + mapFilename
        webbrowser.open_new(url)


# sh = Shapefile("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
# inter, interCheck = sh.getIntersections()
# roads, roadCheck = sh.getRoads()
# sh.plotMap(inter, roads, interCheck, roadCheck)
