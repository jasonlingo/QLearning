# import matplotlib
# matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
# import scipy.integrate as integrate
import matplotlib.animation as animation
from RealMap import RealMap
from Car import *
import threading
import Tkinter as tk
from TrafficSettings import *

class AnimatedMap(threading.Thread):
    """
    A decoration class that draw a animated map based on a RealMap object.
    """

    def __init__(self, realMap):
        """
        Draw a animated map that shows the movement of cars on the map.
        :param map: a map containing roads, intersection, and cars
        :param plt: the pyplot object for drawing the map
        """
        self.realMap = realMap
        self.roads = realMap.getRoads()
        self.intersections = realMap.getIntersections()

        # self.cars = realMap.getCars()
        # self.taxis = realMap.getTaxis()

    def carData(self):
        """
        The method that generates the positions of all cars.
        :return: the cars' positions
        """
        pass

    def plotAnimatedMap(self, fig, ax):
        """
        This method will be continuously run
        :return:
        """
        # self.carPoints, = ax.plot([], [], 'bo', ms=5)
        # self.taxiPoints, = ax.plot([], [], 'yo', ms=5)
        # self.calledTaxiPoints, = ax.plot([], [], 'ro', ms=5)
        # goalLng, goalLat = self.realMap.getGoalPosition()
        # self.goalPoint, = ax.plot([goalLng], [goalLat], 'r*', ms=10)
        self.cnt = 0
        board = self.realMap.getBoard()  #[top, bot, right, left]
        latDiff = board[0] - board[1]
        lngDiff = board[2] - board[3]

        def init():
            """
            The initialization step for drawing a animated map. This will be the base plot
            for the animation.
            """
            print "init animation"

            # plot roads
            for rd in self.roads.values():
                source = rd.getSource()
                target = rd.getTarget()
                if source and target:
                    xs = [source.center.lng, target.center.lng]
                    ys = [source.center.lat, target.center.lat]
                    plt.plot(xs, ys, color='k')

            # initialize markers for cars, taxis, and the goal location
            self.carPoints, = ax.plot([], [], 'bo', ms=5)
            self.taxiPoints, = ax.plot([], [], 'yo', ms=5)
            self.calledTaxiPoints, = ax.plot([], [], 'ro', ms=5)
            goalLng, goalLat = self.realMap.getGoalPosition()
            self.goalPoint, = ax.plot([goalLng], [goalLat], 'r*', ms=10)
            # self.carPoints.set_data([], [])
            # self.calledTaxiPoints.set_data([], [])
            # self.taxiPoints.set_data([], [])
            self.realMap.setAniMapPlotOk(True)

        def animate(i):
            """
            The method is called repeatedly to draw the animation.
            """
            # print "animate", i
            cars = []
            taxis = []
            if self.realMap.checkReset():
                self.carPoints.set_data([], [])
                self.taxiPoints.set_data([], [])
                self.calledTaxiPoints.set_data([], [])
            else:
                cars = self.realMap.getCars().values()
                taxis = self.realMap.getTaxis().values()
            self.carPoints.set_data([car.getCoords()[0] for car in cars], [car.getCoords()[1] for car in cars])
            self.calledTaxiPoints.set_data([taxi.getCoords()[0] for taxi in taxis if taxi.called], [taxi.getCoords()[1] for taxi in taxis if taxi.called])
            self.taxiPoints.set_data([taxi.getCoords()[0] for taxi in taxis if not taxi.called], [taxi.getCoords()[1] for taxi in taxis if not taxi.called])

        ani = animation.FuncAnimation(fig, animate, init_func=init, interval=25, blit=False)
        plt.show()


# =====================================
# For unit testing
# =====================================
# rmap = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
# rmap.addRandomCars(10)
# rmap.addRandomTaxi(5)
# rmap.setRandomGoalPosition()
# amap = AnimatedMap(rmap)
# fig, ax = plt.subplots()
# amap.plotAnimatedMap(fig, ax)



