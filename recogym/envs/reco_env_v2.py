from .abstract import env_args
from .reco_env_v1 import RecoEnv1

# Default arguments for toy environment ------------------------------------

# inherit most arguments from abstract class
env_2_args = {
    **env_args,
    **{
        'K': 5,
        'sigma_omega_initial': 1,
        'sigma_omega': 0.1,
        'number_of_flips': 0,
        'sigma_mu_organic': 3,
        'change_omega_for_bandits': False,
        'normalize_beta': False
    }
}

# Markov states we use in this file:
stop = 2


# Environment definition.
class RecoEnv2(RecoEnv1):

    def __init__(self):
        self.data = []
        self.life_events = []
        self.current_data = []
        self.data_idx = 0
        self.cur_data_idx = 0
        self.product_view = 0
        if 'debug' in env_2_args: self.debug = env_2_args['debug']
        else: self.debug = False
        super(RecoEnv2, self).__init__()

    def update_data(self, data):
        self.data = data
        self.current_data = data[0]
        self.data_idx = 0
        self.cur_data_idx = 0

    def set_static_params(self, data = [], life_events = []):
        self.data = data
        self.current_data = data[0]
        self.life_events = life_events
        super(RecoEnv2, self).set_static_params()

    def draw_click(self, recommendation):
        if self.debug: print('Checking if click for user ', self.data_idx, ' with product ', recommendation,
              ' is contained in future page views: ', self.current_data[self.cur_data_idx:])
        if self.life_events[recommendation] in self.current_data[self.cur_data_idx:]:
            return 1
        else:
            return 0

    def update_product_view(self):
        print('Gladly returning product with ID: ', self.current_data[self.cur_data_idx], ' for user ID: ', self.data_idx)
        self.product_view = int(self.current_data[self.cur_data_idx])
        self.cur_data_idx = self.cur_data_idx + 1

        if self.cur_data_idx >= len(self.current_data) or self.current_data[self.cur_data_idx] == '':
            self.reset(self.data_idx + 1)

    def reset(self, user_id = 0):
        if user_id >= len(self.data):
            self.state = stop
        else:
            self.data_idx = user_id
            self.current_data = self.data[self.data_idx]
            self.cur_data_idx = 0
            super().reset(user_id)
