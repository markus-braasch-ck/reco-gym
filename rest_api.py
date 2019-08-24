from flask import Flask, request
from flask_restful import Resource, Api
import torch as pt

app = Flask(__name__)
api = Api(app)


def flatList(something):
    return [x for sublist in something for x in sublist]
    #flat = np.array(something).flatten()
    #print('flat: ', flat)
    #return np.unique(flat).tolist()
    # if isinstance(something, (list, tuple, set, range)):
    #     for sub in something:
    #         yield from flatten(sub)
    # else:
    #     yield something


class HelloWorld(Resource):
    def __init__(self):
        import gym, recogym
        import sys, os

        module_path = os.path.abspath(os.path.join('recogym'))
        if module_path not in sys.path:
            sys.path.insert(0, module_path)

        # env_0_args is a dictionary of default parameters (i.e. number of products)
        from envs.reco_env_v2 import env_2_args

        from recogym.agents import BanditMFSquare, bandit_mf_square_args
        from recogym.agents import BanditCount, bandit_count_args
        from recogym.agents import RandomAgent, random_args
        from recogym import Configuration

        import csv
        data = list(csv.reader(open("jameson.csv")))[1:5000]
        data = list(map(lambda x: x[0].split(' '), data))
        print('data: ', data[:10])
        life_events = list(filter(lambda z: len(z) > 0, list(map(lambda y: list(filter(lambda x: x < '1000', y)), data))))
        print('life_events before', life_events[:10])
        self.life_events = list(set(self.flatten(life_events)))
        print('life_events after', self.life_events)

        print(len(data), len(data[0]))

        # You can overwrite environment arguments here:
        env_2_args['random_seed'] = 42
        env_2_args['training_data'] = data[1:1000]
        env_2_args['life_events'] = self.life_events
        env_2_args['num_products'] = len(self.life_events)
        print('Number of products: ', env_2_args['num_products'])

        # Initialize the gym for the first time by calling .make() and .init_gym()
        env = gym.make('reco-gym-v2')
        env.init_gym(env_2_args)

        self.agent_banditmfsquare = BanditMFSquare(Configuration({
            **bandit_mf_square_args,
            **env_2_args,
        }))
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
            self.agent_rand.train(old_observation, action, reward, done)
            if env.debug: print(f"Step: {i} - Action: {action} - Observation: {observation.sessions()} - Reward: {reward}")
            i += 1

        self.env = env

    def flatten(self, something):
        if isinstance(something, (list, tuple, set, range)):
            for sub in something:
                yield from self.flatten(sub)
        else:
            yield something

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
        self.env.update_data([json])
        for abc in json:
            action, observation, reward, done, info = self.env.step_offline(observation, reward, done)
            # action = self.agent_rand.act(observation, reward, done)
            print(action)
            actions.append(action['a'])
            # observation, reward, done, info = self.env.step(action['a'])

        print(actions)
        # response = list(map(int, actions[-3:]))
        response = {"response": list(map(lambda x: self.life_events[x], actions[-3:]))}
        print('Sending JSON response: ', response)
        return response


api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)