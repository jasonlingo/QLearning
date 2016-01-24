from Traffic import *
from ControlSignals import ControlSignals


class Intersection(object):
    """
    A class that represents an intersection. It will have a traffic signal control
    to manage when cars can pass through the intersection.
    """

    def __init__(self, corners, center, rect):
        """
        :param corners: the four corners of this intersection
        :param center: the coordinate of the center of this intersection
        :param rect: the area of this intersection
        :return:
        """
        self.corners = corners
        self.center = center
        self.rect = rect
        self.id = Traffic.uniqueId(RoadType.INTERSECTION)
        self.roads = []
        self.inRoads = []
        self.controlSignals = ControlSignals(self)

    # def copy(self, inters):
    #     """
    #     Create a new intersection object according to the given intersection object.
    #     Return the newly created intersection object
    #     :param inters: the intersection to be copied
    #     :return: a new intersection object
    #     """
    #     newInters = Intersection(inters.corners, inters.center, inters.rect)
    #     for rd in inters.getRoad():
    #         newInters.addRoad(rd.copy())

    def update(self):
        for rd in self.roads:
            rd.update()
        result = []
        for ird in self.inRoads:
            result.append(ird.update())
        return result

    def getId(self):
        return self.id

    def getRoads(self):
        return self.roads

    def getInRoads(self):
        return self.inRoads

    def addRoad(self, rd):
        self.roads.append(rd)

    def addInRoad(self, rd):
        self.inRoads.append(rd)