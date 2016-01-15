from Shapefile import Shapefile
from Road import Road
import pygmaps
import webbrowser
import os
import random
# import matplotlib
# matplotlib.use('TKAgg')

from Car import *

class RealMap(object):
    """
    A class that uses real world road data, including the coordinates of road and intersection.
    """

    def __init__(self, shapefileName):
        """
        Initialize a real map according to a
        :param shapefileName:
        :return:
        """
        self.she = Shapefile(shapefileName)
        self.roads = self.she.getRoads()
        self.intersections = self.she.getIntersections()

        self.createMap()
        self.goalLocation = None
        self.board = self.she.getBoard()  #[top, bot, right, left]
        self.cars = {}
        self.taxis = {}

    def createMap(self):
        """
        Connect intersections with roads.
        """
        print "creating map"
        # start_time = time.time() # for computing the execution time
        for inter in self.intersections.values():
            for rd in self.roads.values():
                if rd.isConnected(inter):
                    if not rd.getSource():
                        rd.setSource(inter)  # FIXME: should reduce some distance for intersection
                    elif not rd.getTarget():
                        rd.setTarget(inter)
                        # add a road for opposite direction
                        opRd = Road(rd.corners, rd.center, rd.getTarget(), rd.getSource())
                        self.roads[opRd.id] = opRd
        # print (time.time() - start_time), " seconds"

    def getRoads(self):
        return self.roads

    def getIntersections(self):
        return self.intersections

    def getBoard(self):
        return self.board

    def randomLaneLocation(self):
        """
        Randomly select one road from self.roads and return it.
        :return: the selected location.
        """
        rd = None
        while rd is None:
            tmp = random.choice(self.roads.values())
            if tmp.getSource() and tmp.getTarget():
                rd = tmp
        print rd.lanes
        lane = random.choice(rd.lanes)
        position = random.random()
        return lane, position

    def setRandomGoalPosition(self):
        """
        Assign the goal location.
        :param loc:
        :return:
        """
        lane, position = self.randomLaneLocation()
        self.goalLocation = Trajectory(None, lane, position)

    def getGoalPosition(self):
        return self.goalLocation.getCoords()

    def addRandomCars(self, num):
        """
        Add num cars into the self.cars dictionary by their id. If an id already exists in the dictionary, then
        update the dictionary with the car.
        :param num: the total number of cars to be added into the dictionary
        """
        for i in range(num):
            lane, position = self.randomLaneLocation()
            car = Car(lane, position)
            self.cars[car.id] = car

    def addRandomTaxi(self, num):
        """
        Add num taxis into the self.taxis dictionary by their id. If an id already exists in the dictionary, then
        update the dictionary with this taxi.
        :param num: the total number of taxis to be added into the dictionary
        """
        for i in range(num):
            lane, position = self.randomLaneLocation()
            taxi = Taxi(lane, position)
            self.taxis[taxi.id] = taxi

    def getCars(self):
        return self.cars

    def getTaxis(self):
        return self.taxis

    def moveCar(self):
        """
        update the coordinates of cars
        :return: two lists that contain the x and y coordinates
        """
        pass

    def plotMap(self):
        """
        Plot the map according to the roads and intersections.
        """
        print "plotting map"
        if not self.intersections or not self.roads:
            print "no map to plot"
            return

        inter = self.intersections.values()[0]
        mymap = pygmaps.maps(inter.center[0], inter.center[1], 12)

        for inter in self.intersections.values():
            mymap.addpoint(inter.center[0], inter.center[1], "#0000FF")

        for rd in self.roads.values():
            if rd.getSource() and rd.getTarget():
                mymap.addpath([rd.getSource().center, rd.getTarget().center], "#00FF00")
                # mymap.addpoint(point[0], point[1], "#00FF00")

        mapFilename = "shapefileMap.html"
        mymap.draw('./' + mapFilename)

        # Open the map file on a web browser.
        url = "file://" + os.getcwd() + "/" + mapFilename
        webbrowser.open_new(url)

# class Location(object):
#     """
#     A class that represents a location. It contains the information of the road or intersection id.
#     """
#
#     def __init__(self, coordinates, roadId=None, intersId=None):
#         """
#         :param coordinates: the coordinate of this location
#         :param roadId: if the location is on a road, this records the road id
#                        that this location belongs to
#         :param IntersId: if the intersection is on a intersection, this records the
#                          intersection id this location belongs to
#         """
#         self.coordinates = coordinates
#         self.roadId = roadId
#         self.intersId = intersId
#
#     def equals(self, loc):
#         """
#         Check whether the given location is the same with this location.
#         :param loc: the given location
#         :return: True if the given location is equal to this location; False otherwise
#         """
#         return self.roadId == loc.roadId and self.intersId == loc.intersId and\
#                self.coordinates == loc.coordinates




# =========================================================
# For checking correctness
# =========================================================
# rm = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
#
# rm.plotAnimationMap()
# ani = animation.FuncAnimation(fig, rm.animation, fargs=(particles))