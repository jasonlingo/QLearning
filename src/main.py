from Environment import Environment
from Experiment import Experiment
from Settings import *
from trafficSimulator.RealMap import RealMap
from trafficSimulator.AnimatedMap import AnimatedMap
import threading
import matplotlib.pyplot as plt
import time


if __name__ == '__main__':
    def runExp():
        """
        Perform the learning process for EXP_NUM trials.
        """
        # while not realMap.isAniMapPlotOk():
        #     time.sleep(2)
        for i in range(EXP_NUM):
            print "========== " + str(i+1) + "-th trial =========="
            print "Goal locates at", exp.goalLocation.current.lane.road.id
            exp.startLearning()

        # Print the results
        # experiment.printQValue()
        # experiment.printNSA()
        # experiment.showMap()

    def updateSignal():
        """
        update the traffic signal of each intersection according to the given time interval.
        :param time: (int) second
        """
        print "updating signals"
        signalInterval = 1
        env.updateContralSignal(signalInterval)
        time.sleep(signalInterval)

    # Create a RealMap object and pass it to a Environment object.
    # Start a new thread that runs the learning process.
    realMap = RealMap(SHAPEFILE)
    env = Environment(realMap)
    exp = Experiment(env, TAXI_NUM, CAR_NUM, epsilon=EPSILON, alpha=ALPHA, gamma=GAMMA)
    runExp()

    # Simulation thread
    simulation = threading.Thread(target=runExp)
    simulation.start()
    # signal updating thread
    # signalThread = threading.Thread(target=updateSignal)
    # signalThread.start()

    # plot the animated map
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect(1.0)
    aniMap = AnimatedMap(realMap)
    aniMap.plotAnimatedMap(fig, ax)

    print "Experiments end"
