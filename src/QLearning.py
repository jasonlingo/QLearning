import random
from Settings import MIN_EPSILON

class QLearning(object):
    """
    A Q-learning model.
    """

    def __init__(self, taxi, exp, env, qvalue=None, nsa=None, epsilon=0.1, alpha=0.1, gamma=0.9):
        """
        Args:
            taxi: the assigned taxi
            exp: experiment
            env: the environment for this Q learning to interact with
            qvalue: Q-value table
            nsa: the table records the times of each state that has been reached
            epsilon: a exploration parameter
            alpha: learning rate
            gamma: discounting factor
        Returns:
        """
        self.taxi = taxi
        self.exp = exp
        self.env = env
        self.epsilon = epsilon
        self.defaultEps = epsilon
        self.alpha = alpha
        self.gamma = gamma

        # Q value lookup dictionary
        # {((x, y), action): Q value}
        self.qvalue = qvalue if qvalue is not None else {}

        # record the visited times for state-action
        self.nsa = nsa if nsa is not None else {}

        # for checking oscillation
        self.steps = {}

        self.iteration = 0

    def go(self, second):
        """
        Perform learning procedure.
        """
        oldPos = self.taxi.getPosition().lane.road

        # already at the same road with the goal location
        if self.env.checkArriveGoal(oldPos):
            self.env.setReachGoal(True)
            reward = self.env.getReward(oldPos, oldPos)
            self.learn(oldPos, oldPos, reward, oldPos)
            return

        action = self.chooseAction(oldPos)           # road
        self.taxi.setNextLane(action.lanes[0])
        self.taxi.move(second)
        nextPos = self.taxi.getPosition().lane.road  # current road

        if oldPos != nextPos:
            reward = self.env.getReward(nextPos, action)
            self.learn(oldPos, action, reward, nextPos)

            self.steps[nextPos] = self.steps.get(nextPos, 0) + 1
            if self.steps[nextPos] > 1000:
                print "Oscillation at: ", nextPos, " => ", self.steps[nextPos]

        if self.env.checkArriveGoal(nextPos):
            self.env.setReachGoal(True)

        self.iteration += 1

    def learn(self, state1, action1, reward, state2):
        """
        Args:
            state1: (road)
            action1 (Road): action taken in state1
            reward: (float) reward received after taking action at state1
            state2: (road)
        Returns:
        """
        actions = self.env.getAction(state2)
        maxqnew = max([self.qvalue.get((state2, a), 0.0) for a in actions])
        self.updateQValue(state1, action1, reward, maxqnew)

    def updateQValue(self, state, action, reward, maxqnew):
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
        actions = self.env.getAction(state)  # roads

        if random.random() < self.exp.getEpsilon(self.epsilon, self.iteration):
            action = random.choice(actions)  # exploration
        else:
            q = [self.qvalue.get((state, a), 0.0) for a in actions]
            maxQIdx = q.index(max(q))
            action = actions[maxQIdx]

        return action

    def getTaxi(self):
        return self.taxi
