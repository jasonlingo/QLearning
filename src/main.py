from Environment import Environment
from Experiment import Experiment
from Action import Action
import Settings

if __name__ == '__main__':

    # ========================================================================
    # Initialize training environment
    # ========================================================================
    # Create an environment object
    # actions = [Action.NORTH, Action.SOUTH, Action.EAST, Action.WEST]
    actions = Action.getActions()
    env = Environment(actions, Settings.ENV_BOTTOM, Settings.ENV_TOP, Settings.ENV_LEFT, Settings.ENV_RIGHT)

    # create a learning agent
    exp = Experiment(env, Settings.TAXI_NUM, epsilon=Settings.EPSILON)


    # ========================================================================
    # Start the learning process
    # ========================================================================

    for i in range(Settings.EXP_NUM):
        print "========== " + str(i+1) + "-th trial =========="
        exp.startLearning()

    # experiment.printQValue()
    # experiment.printNSA()
    # experiment.showMap()
