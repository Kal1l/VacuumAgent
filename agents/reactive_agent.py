import random


class ReactiveAgent:
    def select_action(self, percept):
        if percept['current_dirty']:
            return 'CLEAN'
        else:
            actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            return random.choice(actions)
