import numpy as np
import gym
import os
from tqdm import tqdm

total_reward = []
episode = 3000
decay = 0.045


class Agent():
    def __init__(self, env, epsilon=0.05, learning_rate=0.5, GAMMA=0.97, num_bins=7):
        """
        The agent learning how to control the action of the cart pole.

        Hyperparameters:
            epsilon: Determines the explore/expliot rate of the agent
            learning_rate: Determines the step size while moving toward a minimum of a loss function
            GAMMA: The discount factor (tradeoff between immediate rewards and future rewards)
            num_bins: Number of part that the continuous space is to be sliced into.
        """
        self.env = env

        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.gamma = GAMMA

        # self.max_epsilon = 1.0
        # self.min_epsilon = 0.01
        # self.decay_rate = 0.01

        self.num_bins = num_bins
        self.qtable = np.zeros((self.num_bins, self.num_bins,
                               self.num_bins, self.num_bins, self.env.action_space.n))

        # init_bins() is your work to implement.
        self.bins = [
            self.init_bins(-2.4, 2.4, self.num_bins),  # cart position
            self.init_bins(-3.0, 3.0, self.num_bins),  # cart velocity
            self.init_bins(-0.5, 0.5, self.num_bins),  # pole angle
            self.init_bins(-2.0, 2.0, self.num_bins)  # tip velocity
        ]

    def init_bins(self, lower_bound, upper_bound, num_bins):
        """
        Slice the interval into #num_bins parts.

        Parameters:
            lower_bound: The lower bound of the interval.
            upper_bound: The upper bound of the interval.
            num_bins: Number of parts to be sliced.

        Returns:
            a numpy array of #num_bins - 1 quantiles.		

        Example: 
            Let's say that we want to slice [0, 10] into five parts, 
            that means we need 4 quantiles that divide [0, 10]. 
            Thus the return of init_bins(0, 10, 5) should be [2. 4. 6. 8.].

        Hints:
            1. This can be done with a numpy function.
        """
        # Begin your code
        return np.linspace(lower_bound,upper_bound, num_bins + 1)[1:-1]
        #去頭去尾
        
        pass
        # End your code

    def discretize_value(self, value, bins):
        """
        Discretize the value with given bins.

        Parameters:
            value: The value to be discretized.
            bins: A numpy array of quantiles

        returns:
            The discretized value.

        Example:
            With given bins [2. 4. 6. 8.] and "5" being the value we're going to discretize.
            The return value of discretize_value(5, [2. 4. 6. 8.]) should be 2, since 4 <= 5 < 6 where [4, 6) is the 3rd bin.

        Hints:
            1. This can be done with a numpy function.				
        """
        # Begin your code
        return np.digitize(value, bins, right = 'False')
        # return np.searchsorted(bins, value, side = 'right')
        
        pass
        # End your code

    def discretize_observation(self, observation):
        """
        Discretize the observation which we observed from a continuous state space.

        Parameters:
            observation: The observation to be discretized, which is a list of 4 features:
                1. cart position.
                2. cart velocity.
                3. pole angle.
                4. tip velocity. 

        Returns:
            state: A list of 4 discretized features which represents the state.

        Hints:
            1. All 4 features are in continuous space.
            2. You need to implement discretize_value() and init_bins() first
            3. You might find something useful in Agent.__init__()
        """
        # Begin your code
        cart_pos = self.discretize_value(observation[0], self.bins[0])
        cart_v = self.discretize_value(observation[1], self.bins[1])
        pole_angle = self.discretize_value(observation[2], self.bins[2])
        tip_v = self.discretize_value(observation[3], self.bins[3])
        state = [cart_pos, cart_v, pole_angle, tip_v]
        return state

        # End your code

    def choose_action(self, state):
        """
        Choose the best action with given state and epsilon.

        Parameters:
            state: A representation of the current state of the enviornment.
            epsilon: Determines the explore/expliot rate of the agent.
        Returns:
            action: The action to be evaluated.
        """
        # Begin your code
        p = np.random.uniform(0, 1)
        if p < self.epsilon:
            action = self.env.action_space.sample()
        else:
            action = np.argmax(self.qtable[tuple(state)])
        #print(action)
        return action

        # End your code

    def learn(self, state, action, reward, next_state, done):
        """
        Calculate the new q-value base on the reward and state transformation observered after taking the action.

        Parameters:
            state: The state of the enviornment before taking the action.
            action: The exacuted action.
            reward: Obtained from the enviornment after taking the action.
            next_state: The state of the enviornment after taking the action.
            done: A boolean indicates whether the episode is done.

        Returns:
            None (Don't need to return anything)
        """
        # Begin your code
        if done:
            self.qtable[tuple(state)][action] = (1 - self.learning_rate) * self.qtable[tuple(state)][action] + \
            self.learning_rate * reward         
        else:
            self.qtable[tuple(state)][action] = (1 - self.learning_rate) * self.qtable[tuple(state)][action] + \
            self.learning_rate * (reward + self.gamma * np.max(self.qtable[tuple(next_state)]))
        # End your code

        # You can add some conditions to decide when to save your table 
        if done:
            np.save("./Tables/cartpole_table.npy", self.qtable)
            '''
            try:
                pre = np.load("./Tables/cartpole_table.npy")
                pre_avg = np.average(pre)
                obs = self.env.reset()
                state = self.discretize_observation(obs)
                avg_q = np.average(self.qtable[tuple(state)])
                if avg_q > pre_avg:
                    np.save("./Tables/cartpole_table.npy", self.qtable)
            except:
                np.save("./Tables/cartpole_table.npy", self.qtable)
            '''
        
        
    def check_max_Q(self):
        """
        - Implement the function calculating the max Q value of initial state(self.env.reset()).
        - Check the max Q value of initial state

        Parameter:
            self: the agent itself.
            (Don't pass additional parameters to the function.)
            (All you need have been initialized in the constructor.)

        Return:
            max_q: the max Q value of initial state(self.env.reset())
        """
        # Begin your code
        obs = self.env.reset()
        state = self.discretize_observation(obs)
        max_q = np.max(self.qtable[tuple(state)])
        
        power = np.power(self.gamma, 180)
        q = (1 - power) / (1 - self.gamma)
        print("optained_q =", optq)
        
        return max_q
        pass
        # End your code


def train(env):
    """
    Train the agent on the given environment.

    Paramenters:
        env: the given environment.

    Returns:
        None (Don't need to return anything)
    """
    training_agent = Agent(env)
    rewards = []
    for ep in tqdm(range(episode)):
        state = training_agent.discretize_observation(env.reset())
        done = False

        count = 0
        while True:
            count += 1
            action = training_agent.choose_action(state)
            next_observation, reward, done, _ = env.step(action)

            next_state = training_agent.discretize_observation(
                next_observation)

            training_agent.learn(state, action, reward, next_state, done)

            if done:
                rewards.append(count)
                break

            state = next_state

        # training_agent.epsilon = training_agent.min_epsilon + \
        #     (training_agent.max_epsilon - training_agent.min_epsilon) * \
        #     np.exp(-training_agent.decay_rate*(ep + 1))
        if (ep + 1) % 500 == 0:
            training_agent.learning_rate -= decay

    total_reward.append(rewards)


def test(env):
    """
    Test the agent on the given environment.

    Paramenters:
        env: the given environment.

    Returns:
        None (Don't need to return anything)
    """
    testing_agent = Agent(env)

    # Change the filename to your student id
    
        
    testing_agent.qtable = np.load("./Tables/cartpole_table.npy")
    rewards = []

    for _ in range(100):
        state = testing_agent.discretize_observation(testing_agent.env.reset())
        count = 0
        while True:
            count += 1
            action = np.argmax(testing_agent.qtable[tuple(state)])
            next_observation, _, done, _ = testing_agent.env.step(action)

            next_state = testing_agent.discretize_observation(next_observation)

            if done == True:
                rewards.append(count)
                break

            state = next_state

    print(f"average reward: {np.mean(rewards)}")
    print(f"max Q:{testing_agent.check_max_Q()}")


def seed(seed=20):
    '''
    It is very IMPORTENT to set random seed for reproducibility of your result!
    '''
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    # random.seed(seed)


if __name__ == "__main__":
    '''
    The main funtion
    '''
    # Please change to the assigned seed number in the Google sheet
    SEED = 69

    env = gym.make('CartPole-v0')
    seed(SEED)
    env.seed(SEED)
    env.action_space.seed(SEED)

    if not os.path.exists("./Tables"):
        os.mkdir("./Tables")

   # training section:
    for i in range(5):
        print(f"#{i + 1} training progress")
        train(env)
    # testing section:
    test(env)

    if not os.path.exists("./Rewards"):
        os.mkdir("./Rewards")

    np.save("./Rewards/cartpole_rewards.npy", np.array(total_reward))

    env.close()
