from Shapefile import Shapefile
from Road import Road
from Traffic import *
import pygmaps
import webbrowser
import os


class RealMap:
    """
    A class that uses real world road data, including the coordinates of road and intersection.
    """

    def __init__(self, shapefileName):
        self.she = Shapefile(shapefileName)
        self.roads = self.she.getRoads()
        self.intersections = self.she.getIntersections()

    def createMap(self):
        """
        Connect intersections with roads.
        """
        for inter in self.intersections:
            for rd in self.roads:
                if rd.isConnected(inter):
                    if not rd.getSource():
                        rd.setSource(inter)
                    elif not rd.getTarget():
                        rd.setTarget(inter)
                        # add a road for opposite direction
                        self.roads.append(Road(rd.corners, rd.center, rd.getTarget(), rd.getSource()))

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



# test
rm = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
rm.createMap()
rm.plotMap()