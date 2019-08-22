from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def __init__(self):
        import gym, recogym
        import sys, os

        module_path = os.path.abspath(os.path.join('recogym'))
        if module_path not in sys.path:
            sys.path.insert(0, module_path)

        # env_0_args is a dictionary of default parameters (i.e. number of products)
        from envs.reco_env_v2 import env_2_args

        # from recogym.agents import BanditMFSquare, bandit_mf_square_args
        from recogym.agents import BanditCount, bandit_count_args
        from recogym.agents import RandomAgent, random_args
        from recogym import Configuration

        import csv
        data = list(csv.reader(open("data.csv")))
        print(len(data), len(data[0]))

        # You can overwrite environment arguments here:
        env_2_args['random_seed'] = 42
        env_2_args['training_data'] = data
        env_2_args['num_products'] = int(max(map(max, env_2_args['training_data'])).strip())

        # Initialize the gym for the first time by calling .make() and .init_gym()
        env = gym.make('reco-gym-v2')
        env.init_gym(env_2_args)

        # self.agent_banditmfsquare = BanditMFSquare(Configuration({
        #     **bandit_mf_square_args,
        #     **env_2_args,
        # }))
        self.agent_banditcount = BanditCount(Configuration({
            **bandit_count_args,
            **env_2_args,
        }))
        self.agent_rand = RandomAgent(Configuration({
            **random_args,
            **env_2_args,
        }))

        # .reset() env before each episode (one episode per user).
        env.reset()

        # Counting how many steps.
        i = 0

        observation, reward, done = None, 0, False
        while not done:
            old_observation = observation
            action, observation, reward, done, info = env.step_offline(observation, reward, done)
            self.agent_banditcount.train(old_observation, action, reward, done)
            print(f"Step: {i} - Action: {action} - Observation: {observation.sessions()} - Reward: {reward}")
            i += 1

        self.env = env

    def get(self):
        return {'hello': 'world'}

    def post(self):
        json = request.get_json()
        print(json)

        self.env.reset()
        observation, _, done, _ = self.env.step(None)
        reward = None
        done = None
        actions = []
        for pageId in json:
            action = self.agent_banditcount.act(observation, reward, done)
            actions.append(action['a'])
            observation, reward, done, info = self.env.step(action['a'])

        response = list(map(int, actions))
        print('Sending JSON response: ', response)
        return response


api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)