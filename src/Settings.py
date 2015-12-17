NORTH = "North"
SOUTH = "South"
EAST = "East"
WEST = "West"



EXP_NUM = 30000                                        # total number of trials
TAXI_NUM = 1                                           # total number of taxis
ENV_BOTTOM = 0                                         # the bottom limit of the experiment region
ENV_TOP = 50                                           # the top limit of the experiment region
ENV_LEFT = 0                                           # the left limit of the experiment region
ENV_RIGHT = 50                                         # the right limit of the experiment region
SUB_REGION_NUM = max(ENV_TOP * ENV_RIGHT / 50, 1)      # the number of sub-regions in the map
MAX_SUB_REGION_SIDE = min(ENV_TOP, ENV_RIGHT) / 5      # the maximum length of side for sub-region
DELETE_ROAD_NUM = ENV_TOP * ENV_RIGHT / 4              # determine the road density
GOAL_REWARD = 1000                                     # reward for reaching goal
UNIT_TIME = 0.05                                       # used to calculate the distance the taxi can go in a time step
EPSILON = 0.15                                         # the exploration parameter