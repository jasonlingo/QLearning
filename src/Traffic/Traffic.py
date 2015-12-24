from random import shuffle
from math import radians, cos, sin, asin, sqrt


# ===============================================
# Settings
# ===============================================
METER_TYPE = "K"
"""Use kilometer (K) or mile (M) for the haversine function"""
EARTH_RADIUS_MILE = 3959.0
"""The radius of the earth in miles"""
EARTH_RADIUS_KM = 6371.0
"""The radius of the earth in kilometers"""

GRID_SIZE = 32
DEFAULT_TIME_FACTOR = 5
LIGHT_FLIP_INTERVAL = 20
CARS_NUMBER = 100
TAXI_NUMBER = 20


class Traffic:
    uniqueid = 0

    @staticmethod
    def sample(obj, n):
        """
        return a shuffled sub-list of objects
        :param obj: the given list
        :param n: the number of samples
        :return: a list of random samples
        """
        return Traffic.shuffle(obj)[0:max(0, n)]

    @staticmethod
    def shuffle(obj):
        """
        Shuffle a given list and return a shuffled list.
        First create a copy of the original list in order
        to prevent that the original list will be affected
        by the shuffle operation.
        :param obj: the given list
        :return: a shuffled list
        """
        shuffled = obj[:]
        shuffle(shuffled)
        return shuffled

    @classmethod
    def uniqueID(cls, idType):
        cls.uniqueid += 1
        return idType + "_" + str(cls.uniqueid)


class RoadType:
    ROAD = "Road"
    INTERSECTION = "Intersection"


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    Args:
      (tuple) poitn1: the position of the first point
      (tuple) point2: the position of the second point
    Return:
      (float) distance (in km) between two nodes
    """
    # Convert decimal degrees to radians
    lat1, lng1 = point1
    lat2, lng2 = point2
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))

    # The radius of earth in kilometers.
    if METER_TYPE == "K":
        r = EARTH_RADIUS_KM    # The radius of earth in kilometers.
    else:
        r = EARTH_RADIUS_MILE  # The radius of earth in miles.
    return c * r
