import random


class ModelBasedAgent:
    def __init__(self):
        self.visited = set()
        self.cleaned = set()
        self.pos = (0, 0)

    def select_action(self, percept):
        y, x = self.pos
        self.visited.add((y, x))
        if percept['current_dirty']:
            self.cleaned.add((y, x))
            return 'CLEAN'
        # Prefer unvisited moves
        for move in percept['possible_moves']:
            new_pos = self._get_new_pos(move)
            if new_pos not in self.visited:
                self.pos = new_pos
                return move
        # Otherwise, move randomly
        move = random.choice(percept['possible_moves'])
        self.pos = self._get_new_pos(move)
        return move

    def _get_new_pos(self, move):
        y, x = self.pos
        if move == 'UP': return (y-1, x)
        if move == 'DOWN': return (y+1, x)
        if move == 'LEFT': return (y, x-1)
        if move == 'RIGHT': return (y, x+1)
        return (y, x)
