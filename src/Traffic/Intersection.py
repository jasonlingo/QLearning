from Traffic import *
from ControlSignals import ControlSignals


class Intersection:
    """
    A class that represents an intersection. It will have a traffic signal control
    to manage when cars can pass through the intersection.
    """

    def __init__(self, corners, center):
        """

        :param corners:
        :param center:
        :return:
        """
        self.corners = corners
        self.center = center
        self.id = Traffic.uniqueID(RoadType.INTERSECTION)
        self.roads = []
        self.inRoads = []
        self.controlSignals = ControlSignals()
