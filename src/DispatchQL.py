from QLearning import QLearning
import random
from Settings import CHECK_INTERVAL

class DispatchQL(QLearning):
    """
    A Q-learning algorithm for learning dispatching policy
    """

    def __init__(self, allTaxis, availableTaxis, environment, qvalue, nsa, experiment, epsilon=0.1, alpha=0.1, gamma=0.9):
        """
        Args:
            taxis      : all taxis on the environment
            environment: the environment for this Q learning to interact with
            qvalue     : Q-value table
            nsa        : the table records the times of each state that has been reached
            epsilon    : a exploration parameter
            alpha      : learning rate
            gamma      : discounting factor
        Returns:
        """
        self.allTaxis = allTaxis
        self.availableTaxis = availableTaxis
        self.env = environment
        self.experiment = experiment
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

        # Q value lookup dictionary
        # {((x, y), action): Q value}
        self.qvalue = qvalue

        # record the visited times for state-action
        self.nsa = nsa

        # for checking oscillation
        self.steps = []

        # record data for one trial
        self.stateAction = {}
        self.trialTime = 0
        self.taxiTrafficTime = {}

    def go(self, interval):
        """
        Perform learning procedure.
        action: a nearest taxi
        state: the taxis' position (by road id)
        :param interval: second
        """
        self.addTime(interval)

        oldState = self.getState()     # list all the available taxis' positions
        action = self.chooseAction()   #

        taxi, trafficTime = self.experiment.findFastestTaxi()
        if not self.experiment.isQuicker(taxi, CHECK_INTERVAL):
            taxi = None

        # self.stateAction[(tuple(oldState), action)] = self.trialTime  # the time for the chosen taxi to arrive the goal location after this action is called
        if taxi not in self.taxiTrafficTime:
            self.taxiTrafficTime[taxi] = trafficTime

        # goal already reached
        if self.env.isGoalReached():
            reward = self.getReward()
            self.learn(oldState, None, reward, oldState)
            self.resetTrial()
            return

        nextState = self.getState()

        if oldState != nextState:
            reward = self.env.getReward(nextState, action)

            self.steps.append(nextState)
            if self.steps.count(nextState) > 1000:
                print "Oscillation at: ", nextState, " => ", self.steps.count(nextState)

            # self.taxi.setPosition(nextPos)
            self.learn(oldState, action, reward, nextState)

    def getState(self):
        return sorted([taxi.trajectory.current.lane.road.id for taxi in self.allTaxis if taxi.isAvailable() or taxi.isCalled()])

    def getActions(self):
        pass

    def getReward(self):
        # if self.env.isGoalReached():
        pass
        return  # TODO

    def addTime(self, second):
        self.trialTime += second

    def resetTrial(self):
        self.trialTime = 0
        self.stateAction = {}

    def learn(self, state1, action1, reward, state2):
        """
        Args:
            state1: (road)
            action1 (Road): action taken in state1
            reward: (float) reward received after taking action at state1
            state2: (road)
        Returns:
        """
        actions = self.getActions()
        maxqnew = max([self.qvalue.get((state2, a), 0.0) for a in actions])
        self.updateQValue(state1, action1, reward, maxqnew)

    def updateQValue(self, state, action, reward, maxqnew):
        """
        Args:
            state:
            action:
            reward:
            maxqnew:
        Returns:
        """
        self.nsa[(state, action)] = self.nsa.get((state, action), 0) + 1
        oldv = self.qvalue.get((state, action), 0.0)
        self.qvalue[(state, action)] = oldv + self.alpha * (reward + self.gamma * maxqnew - oldv)
        # TODO: take the nsa into account when update q vaule

    def chooseAction(self, state):
        """
        Randomly choose an action if the random variable is less than the
        epsilon. Or choose the action that has the highest q value of the
        given state.
        Args:
            pos: LanePosition
        Returns:
            a chosen action
        """
        if random.random() < self.epsilon:
            # print "@",
            action = random.choice(self.taxis)  # exploration
        else:
            beenPos = False
            # for a in actions: # FIXME
            #     if self.getQValue(state, a) > 0:
            #         beenPos = True
            #         break
            if True or beenPos: # FIXME
                # print "*",
                # q = [self.getQValue(state, a) for a in actions]
                q = [self.qvalue.get((state, a), 0.0) for a in actions]
                maxQIdx = q.index(max(q))
                action = actions[maxQIdx]
            # else:
            #     print "?",
            #     # provide information for choosing an action
            #     fastestTime = sys.maxint
            #     action = None
            #     for a in actions:
            #         if a == Settings.NORTH:
            #             time = self.env.map.trafficTime((pos[0], pos[1]+1), self.env.getGoalLocation(), a)
            #         elif a == Settings.SOUTH:
            #             time = self.env.map.trafficTime((pos[0], pos[1]-1), self.env.getGoalLocation(), a)
            #         elif a == Settings.EAST:
            #              time = self.env.map.trafficTime((pos[0]+1, pos[1]), self.env.getGoalLocation(), a)
            #         elif a == Settings.WEST:
            #              time = self.env.map.trafficTime((pos[0]-1, pos[1]), self.env.getGoalLocation(), a)
            #
            #         if time < fastestTime:
            #             fastestTime = time
            #             action = a
        return action

    def getTaxi(self):
        return self.taxi