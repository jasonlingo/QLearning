from Traffic import *
from Car import *


class World:
    """
    A class that manages all the tasks and objects of the traffic simulator.
    """

    def __init__(self):
        self.toRemove = []
        self.onTick = Traffic.bind(self.onTick, self)
        self.cars = None
        self.taxis = None
        self.roads = None
        self.intersections = None
        self.carsNumber = CARS_NUMBER

    def instantSpeed(self):
        """
        Calculate the average speed of all the cars.
        :return: average speed
        """
        if not self.cars and not self.taxis: # no car and taxi
            return 0

        speed = [car.speed for car in self.cars] + [taxi.speed for taxi in self.taxis]
        return sum(speed) / float(len(speed))

    def initialize(self, obj):
        """
        Create intersection, roads, cars, and taxis
        :param obj:
        :return:
        """
        if not obj:
            obj = {}

        self.intersections = Pool(Intersection, obj.Intersections)
        self.roads = Pool(Road, obj.roads)
        self.cars = Pool(Car, obj.cars)
        self.taxis = Pool(Taxi, obj.taxis)
        self.carsNumber = 0
        return self.carsNumber

    def generateMap(self):





    def onTick(self):
        """
        Control the time frame and refresh the traffic signals and cars' movement.
        """

        # change traffic signal


        # change cars' position


    def refreshCar(self):
        """
        When some cars are disappeared because they are located outside the map, add
        new cars into the map. If the number of cars is more than the limit, remove
        some cars randomly.
        """
        if len(self.cars) < CARS_NUMBER:
            self.addRandomCar(CARS_NUMBER - len(self.cars))
        elif len(self.cars) > CARS_NUMBER:
            self.removeRandomCar(len(self.cars) - CARS_NUMBER)

        if len(self.cars) < TAXI_NUMBER:
            self.addRandomTaxi(TAXI_NUMBER - len(self.cars))
        elif len(self.cars) > TAXI_NUMBER:
            self.removeRandomTaxi(len(self.cars) - TAXI_NUMBER)

    def addRoad(self, road):
        self.roads.append(road)
        road.source.roads.push(road)
        road.target.inRoads.push(road)
        return road.update()

    def getRoad(self, id):
        return self.roads.get(id)

    def addCar(self, car):
        self.cars.append(car)

    def getCar(self, id):
        return self.cars.get(id)

    def addTaxi(self, taxi):
        self.taxis.append(taxi)

    def getTaxi(self, id):
        return self.taxis.get(id)

    def removeCar(self, car):
        self.toRemove.append(car.id)
        return self.cars.pop(car)

    def clearTmpRemove(self):
        self.toRemove = []

    def addIntersection(self, intersection):
        self.intersections.append(intersection)

    def getIntersection(self, id):
        return self.intersections.get(id)

    def addRandomCar(self):
        road = Traffic.sample(self.roads.all())
        if road:
            lane = Traffic.sample(road.lanes)
            if lane:
                self.addCar(Car(50, lane, 0))

