import random
from collections import deque


class ModelBasedAgent:
    def __init__(self):
        self.pos = (0, 0)
        self.visited = set()
        self.obstacles = set()
        self.map = {}  # {(y, x): {'visited': bool, 'obstacle': bool}}
        self.returning_home = False
        self.home_path = []

    def select_action(self, percept):
        y, x = self.pos
        self.visited.add((y, x))
        self.map[(y, x)] = self.map.get((y, x), {'visited': False, 'obstacle': False})
        self.map[(y, x)]['visited'] = True

        # Marca obstáculos ao redor
        for move in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            ny, nx = self._get_new_pos(move)
            if move not in percept['possible_moves']:
                self.obstacles.add((ny, nx))
                self.map[(ny, nx)] = self.map.get((ny, nx), {'visited': False, 'obstacle': False})
                self.map[(ny, nx)]['obstacle'] = True

        # Limpa se estiver sujo
        if percept['current_dirty']:
            return 'CLEAN'

        # Movimentos para locais não visitados e não obstáculos
        unvisited_moves = []
        for move in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            ny, nx = self._get_new_pos(move)
            if move in percept['possible_moves']:
                if not self.map.get((ny, nx), {'visited': False, 'obstacle': False})['visited'] and not self.map.get((ny, nx), {'visited': False, 'obstacle': False})['obstacle']:
                    unvisited_moves.append(move)

        if unvisited_moves and not self.returning_home:
            move = random.choice(unvisited_moves)
            self.pos = self._get_new_pos(move)
            return move

        # Se não há locais não visitados acessíveis, verifica se há locais não visitados no mapa
        all_known_positions = set(self.map.keys())
        not_visited = [pos for pos in all_known_positions if not self.map[pos]['visited'] and not self.map[pos]['obstacle']]
        if not_visited and not self.returning_home:
            # Tenta encontrar caminho até algum não visitado
            path = self._shortest_path(self.pos, not_visited)
            if path and len(path) > 1:
                next_pos = path[1]
                move = self._move_to_pos(next_pos)
                if move and move in percept['possible_moves']:
                    self.pos = next_pos
                    return move

        # Se não há mais locais não visitados, retorna à posição inicial pelo caminho mais curto
        if not self.returning_home and (not unvisited_moves and not not_visited):
            self.returning_home = True
            self.home_path = self._shortest_path(self.pos, [(0, 0)])
            if self.home_path and len(self.home_path) > 1:
                self.home_path = self.home_path[1:]

        if self.returning_home and self.home_path:
            next_pos = self.home_path[0]
            move = self._move_to_pos(next_pos)
            if move and move in percept['possible_moves']:
                self.pos = next_pos
                self.home_path.pop(0)
                return move
            else:
                # Se não pode seguir o caminho, tenta qualquer movimento possível
                possible = [m for m in percept['possible_moves']]
                if possible:
                    move = random.choice(possible)
                    self.pos = self._get_new_pos(move)
                    return move

        # Se nada mais, faz movimento aleatório permitido
        possible = [m for m in percept['possible_moves']]
        if possible:
            move = random.choice(possible)
            self.pos = self._get_new_pos(move)
            return move

        return 'CLEAN'

    def _get_new_pos(self, move):
        y, x = self.pos
        if move == 'UP': return (y-1, x)
        if move == 'DOWN': return (y+1, x)
        if move == 'LEFT': return (y, x-1)
        if move == 'RIGHT': return (y, x+1)
        return (y, x)

    def _move_to_pos(self, target_pos):
        y, x = self.pos
        ty, tx = target_pos
        if ty < y: return 'UP'
        if ty > y: return 'DOWN'
        if tx < x: return 'LEFT'
        if tx > x: return 'RIGHT'
        return None

    def _shortest_path(self, start, goals):
        # BFS para o caminho mais curto até qualquer posição em goals
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            current, path = queue.popleft()
            if current in goals:
                return path
            for move in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                ny, nx = self._get_pos_from(current, move)
                if self.map.get((ny, nx), {'obstacle': False})['obstacle']:
                    continue
                if (ny, nx) not in visited:
                    visited.add((ny, nx))
                    queue.append(((ny, nx), path + [(ny, nx)]))
        return None

    def _get_pos_from(self, pos, move):
        y, x = pos
        if move == 'UP': return (y-1, x)
        if move == 'DOWN': return (y+1, x)
        if move == 'LEFT': return (y, x-1)
        if move == 'RIGHT': return (y, x+1)
        return (y, x)

# O agente modelo agora:
# - Mantém um mapa interno das células visitadas e limpas, mas não sabe onde estão os obstáculos.
# - Prioriza limpar a célula atual se estiver suja.
# - Prioriza movimentos para células não visitadas acessíveis.
# - Se não há células não visitadas acessíveis, segue um caminho sistemático (ziguezague) para explorar o ambiente.
# - Se não encontra células não visitadas, comporta-se como um agente reativo simples, tentando movimentos aleatórios válidos.
# - Não sabe quantas sujeiras existem no ambiente e não depende de limpar tudo para decidir suas ações.
# - Não utiliza conhecimento prévio de obstáculos, apenas evita movimentos bloqueados conforme informado pelo ambiente.
# - O agente retorna à posição inicial apenas se a simulação exigir, mas não faz planejamento para isso após limpar tudo.
# - O comportamento é de exploração eficiente, priorizando novas células, mas pode revisitar antigas se necessário.

