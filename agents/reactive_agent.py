import random


class ReactiveAgent:
    def select_action(self, percept):
        if percept['current_dirty']:
            return 'CLEAN'
        else:
            actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            # Tenta qualquer direção, mas penalidade só conta se movimento for possível
            return random.choice(actions)
