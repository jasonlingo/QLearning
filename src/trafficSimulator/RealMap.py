from Shapefile import Shapefile
from Road import Road
from Car import *
import pygmaps
import webbrowser
import os
import time


class RealMap(object):
    """
    A class that uses real world road data, including the coordinates of road and intersection.
    """

    def __init__(self, shapefileName):
        """
        1. Initialize a real map according to a shapefile.
        2. Get the information of road and intersection from the parsed shapefile.
        3. Create a map by connecting roads with intersections.
        4. Randomly initialize a goal position

        :param shapefileName: the file name of the given shapefile
        """

        self.she = Shapefile(shapefileName)
        self.roads = self.she.getRoads()
        self.intersections = self.she.getIntersections()
        self.createMap()
        self.board = self.she.getBoard()  #[top, bot, right, left] of this map

        self.goalLocation = None
        self.setRandomGoalPosition()
        self.cars = {}
        self.taxis = {}
        self.reset = False
        self.locDict = defaultdict(list)
        self.aniMapPlotOK = False

    def createMap(self):
        """
        Connect intersections with roads. Assume every road has two directions.
        """
        print "creating map",

        i = 0
        start_time = time.time()  # for computing the execution time
        for inter in self.intersections.values():
            for rd in self.roads.values():
                i += 1
                if i % 1000000 == 0:
                    print ".",
                    if i % 50000000 == 0:
                        print ""

                if rd.isConnected(inter):
                    if not rd.getSource():
                        rd.setSource(inter)  # FIXME: reduce some distance for intersection?
                        inter.addRoad(rd)
                    elif not rd.getTarget():
                        rd.setTarget(inter)
                        inter.addInRoad(rd)
                        # add a road for opposite direction
                        opRd = Road(rd.corners, rd.center, rd.getTarget(), rd.getSource())
                        inter.addRoad(opRd)
                        rd.getSource().addInRoad(opRd)
                        self.roads[opRd.id] = opRd
        print ""
        removeRoads = []
        removeInters = []

        for inter in self.intersections.values():
            if len(inter.getInRoads()) == 0 or len(inter.getRoads()) == 0:
                removeInters.append(inter)

        for rd in self.roads.values():
            if not rd.getSource() or not rd.getTarget():
                removeRoads.append(rd)

        print "remove", len(removeRoads), "roads and", len(removeInters), "intersections"
        for inter in removeInters:
            del self.intersections[inter.id]
        for rd in removeRoads:
            del self.roads[rd.id]

        print (time.time() - start_time), " seconds"

        print "checking map"
        for road in self.roads.values():
            if road.getTarget() and road.getSource():
                if len(road.lanes) == 0:
                    print "road error, no lane on a road"
        for inter in self.intersections.values():
            if len(inter.getRoads()) == 0:
                print "intersection has no road"
        print "end checking"


    def getRoads(self):
        return self.roads

    def getIntersections(self):
        return self.intersections

    def getBoard(self):
        return self.board

    def randomLaneLocation(self):
        """
        Randomly select one land from a randomly selected road and position (the distance from
        the source point to the picked position.
        :return: the selected lane and position.
        """
        rd = None
        while rd is None:
            tmp = random.choice(self.roads.values())
            if tmp.getSource() and tmp.getTarget():
                rd = tmp
        lane = random.choice(rd.lanes)
        position = random.random() * lane.length
        return lane, position

    def setRandomGoalPosition(self):
        """
        Assign the goal location.
        :param loc:
        :return:
        """
        lane, position = self.randomLaneLocation()
        self.goalLocation = Trajectory(None, lane, position)
        self.goalLocation.setGoal()
        return self.goalLocation

    def getGoalPosition(self):
        return self.goalLocation.getCoords()

    def getGoalLanePosition(self):
        return self.goalLocation

    def clearTaxis(self):
        self.taxis = {}

    def clearCars(self):
        self.cars = {}

    def addRandomCars(self, num):
        """
        Add num cars into the self.cars dictionary by their id. If an id already exists in the dictionary, then
        update the dictionary with the car.
        :param num: the total number of cars to be added into the dictionary
        """
        while len(self.cars) < num:
            lane, position = self.randomLaneLocation()
            if self.checkOverlap(lane, position):
                car = Car(lane, position)
                self.cars[car.id] = car

    def addRandomTaxi(self, num):
        """
        Add num taxis into the self.taxis dictionary by their id. If an id already exists in the dictionary, then
        update the dictionary with this taxi.
        :param num: the total number of taxis to be added into the dictionary
        """
        while len(self.taxis) < num:
            lane, position = self.randomLaneLocation()
            if self.checkOverlap(lane, position):
                taxi = Taxi(lane, position)
                self.taxis[taxi.id] = taxi

    def checkOverlap(self, lane, position):
        """
        Check whether the picked position for a car is overlapped with existing cars.
        :param locDict: the dictionary records all the cars' position on each lane
        :param lane: the given lane to check
        :param position: the given position to check
        :return: True if the car is not overlapped with existing cars; False otherwise
        """
        half = 0.0025 / lane.length  # TODO: consider different car length
        for (start, end) in self.locDict[lane]:
            if start <= position + half <= end or start <= position - half <= end:
                return False
        self.locDict[lane].append((position - half, position + half))
        return True

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

    def setResetFlag(self, b):
        self.reset = b
        self.locDict = defaultdict(list)

    def checkReset(self):
        return self.reset

    def setAniMapPlotOk(self, b):
        self.aniMapPlotOK = b

    def isAniMapPlotOk(self):
        return self.aniMapPlotOK

    def changeContralSignal(self, delta):
        for inter in self.intersections.values():
            inter.controlSignals.onTick(delta)
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