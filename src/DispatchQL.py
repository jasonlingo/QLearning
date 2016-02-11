from QLearning import QLearning


class DispatchQL(QLearning):
    """
    A Q-learning algorithm for learning dispatching policy
    """

    def __init__(self, traffic, environment, qvalue={}, nsa={}, epsilon=0.1, alpha=0.1, gamma=0.9):
        """
        Args:
            taxi: the assigned taxi
            environment: the environment for this Q learning to interact with
            qvalue: Q-value table
            nsa: the table records the times of each state that has been reached
            epsilon: a exploration parameter
            alpha: learning rate
            gamma: discounting factor
        Returns:
        """
        self.traffic = traffic
        self.env = environment
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

        action = self.chooseAction(oldPos)  # road
        self.taxi.setNextLane(action.lanes[0])
        self.taxi.move(second)
        nextPos = self.taxi.getPosition().lane.road  # current road

        # nextPos = self.env.nextPos(self.taxi, action)
        # TODO
        # minus = 0
        # if (self.env.map.findRoad(oldPos), action) in self.nsa:
        #     minus = self.nsa[(self.env.map.findRoad(oldPos), action)] * 0.1
        # reward = self.env.getReward(nextPos, action) - minus
        if oldPos != nextPos:
            reward = self.env.getReward(nextPos, action)

            self.steps.append(nextPos)
            if self.steps.count(nextPos) > 1000:
                print "Oscillation at: ", nextPos, " => ", self.steps.count(nextPos)

            # self.taxi.setPosition(nextPos)
            self.learn(oldPos, action, reward, nextPos)

        if self.env.checkArriveGoal(nextPos):
            self.env.setReachGoal(True)

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
        # state1 = self.env.map.findRoad(state1)
        # state2 = self.env.map.findRoad(state2)

        # maxqnew = max([self.getQValue(state2, a) for a in actions])
        maxqnew = max([self.qvalue.get((state2, a), 0.0) for a in actions])
        # self.updateQValue(state1, action1, reward, reward + self.gamma * maxqnew)
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
        actions = self.env.getAction(state)  # roads

        if random.random() < self.epsilon:
            # print "@",
            action = random.choice(actions)  # exploration
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

    # def getQValue(self, state, action):
    #     """
    #
    #     Args:
    #         state: (x, y)
    #         action: the chosen action
    #     Returns:
    #         the state-action Q value
    #     """
    #     return self.qvalue.get((state, action), 0.0)  # if the key cannot be found, return 0.0

    def getTaxi(self):
        return self.taxi