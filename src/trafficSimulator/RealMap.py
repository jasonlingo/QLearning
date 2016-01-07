from Shapefile import Shapefile
from Road import Road
from Traffic import *
import pygmaps
import webbrowser
import os
import random

class RealMap(object):
    """
    A class that uses real world road data, including the coordinates of road and intersection.
    """

    def __init__(self, shapefileName):
        self.she = Shapefile(shapefileName)
        self.roads = self.she.getRoads()
        self.intersections = self.she.getIntersections()
        self.createMap()
        self.goalLocation = None

    def createMap(self):
        """
        Connect intersections with roads.
        """
        for inter in self.intersections:
            for rd in self.roads:
                if rd.isConnected(inter):
                    if not rd.getSource():
                        rd.setSource(inter)  # FIXME: should reduce some distance for intersection
                    elif not rd.getTarget():
                        rd.setTarget(inter)
                        # add a road for opposite direction
                        self.roads.append(Road(rd.corners, rd.center, rd.getTarget(), rd.getSource()))

    def randomRoadLocation(self):
        """
        Randomly select one road or intersection from the road or intersection set,
        then pick a random coordinates from the selected road or the center of the
        selected intersection.
        :return: the selected location.
        """
        if random.random() >= 0.5:
            candidate = random.choice(self.roads)
            source = candidate.source.center
            target = candidate.target.center
            portion = random.random()
            coors = (source[0] + (target[0] - source[0]) * portion, \
                     source[1] + (target[1] - source[1]) * portion)
            loc = Location(coors, candidate.id, None)
        else:
            candidate = random.choice(self.intersections)
            coors = candidate.center
            loc = Location(coors, None, candidate.id)
        return loc

    def setGoalLocation(self, loc):
        """

        :param loc:
        :return:
        """
        self.goalLocation = loc

    def plotMap(self):
        # print "Total points:", len(intersections) + len(roads)
        if not self.intersections and not self.roads:
            print "no map to plot"
            return

        mymap = pygmaps.maps(self.intersections[0].center[0], self.intersections[0].center[1], 12)

        for inter in self.intersections:
            mymap.addpoint(inter.center[0], inter.center[1], "#0000FF")

        for rd in self.roads:
            if rd.getSource() and rd.getTarget():
                mymap.addpath([rd.getSource().center, rd.getTarget().center], "#00FF00")
                # mymap.addpoint(point[0], point[1], "#00FF00")

        mapFilename = "shapefileMap.html"
        mymap.draw('./' + mapFilename)

        # Open the map file on a web browser.
        url = "file://" + os.getcwd() + "/" + mapFilename
        webbrowser.open_new(url)



class Location(object):
    """
    A class that represents a location. It contains the information of the road or intersection id.
    """

    def __init__(self, coordinates, roadId=None, intersId=None):
        """
        :param coordinates: the coordinate of this location
        :param roadId: if the location is on a road, this records the road id
                       that this location belongs to
        :param IntersId: if the intersection is on a intersection, this records the
                         intersection id this location belongs to
        """
        self.coordinates = coordinates
        self.roadId = roadId
        self.intersId = intersId

    def equals(self, loc):
        """
        Check whether the given location is the same with this location.
        :param loc: the given location
        :return: True if the given location is equal to this location; False otherwise
        """
        return self.roadId == loc.roadId and self.intersId == loc.intersId and\
               self.coordinates == loc.coordinates


# test
# rm = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
# rm.createMap()
# rm.plotMap()