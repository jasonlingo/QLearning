from Environment import Environment
from Experiment import Experiment
from Settings import *
from trafficSimulator.RealMap import RealMap
from trafficSimulator.World import World

if __name__ == '__main__':

    # ========================================================================
    # Initialize training environment
    # ========================================================================
    # Create a traffic simulator and pass it to the Environment() class.
    trafficSimulator = World(SHAPEFILE)
    env = Environment(trafficSimulator)

    # create a learning trial
    exp = Experiment(env, TAXI_NUM, CAR_NUM, epsilon=EPSILON, alpha=ALPHA, gamma=GAMMA)


    # ========================================================================
    # Start the learning process
    # ========================================================================
    for i in range(EXP_NUM):
        print "========== " + str(i+1) + "-th trial =========="
        exp.startLearning()

    # experiment.printQValue()
    # experiment.printNSA()
    # experiment.showMap()
