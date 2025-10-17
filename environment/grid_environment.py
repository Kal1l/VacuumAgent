import random

class GridEnvironment:
    """
    Ambiente em grade para simulação de agentes aspiradores.
    Representa um mundo 2D com sujeira e obstáculos.
    """

    def __init__(self, width, height, dirt_prob=0.3, obstacle_prob=0.1):
        """
        Inicializa o ambiente com dimensões e probabilidades especificadas.
        
        Args:
            width: Largura do ambiente
            height: Altura do ambiente
            dirt_prob: Probabilidade de cada célula estar suja
            obstacle_prob: Probabilidade de cada célula ter obstáculo
        """

        self.width = width
        self.height = height
        self.grid = [[random.random() < dirt_prob for _ in range(width)] for _ in range(height)]
        self.obstacles = [[random.random() < obstacle_prob for _ in range(width)] for _ in range(height)]
        self.agent_pos = (0, 0)
        # Garante que a posição inicial não é obstáculo
        self.obstacles[0][0] = False
        # Garante que pelo menos uma saída da posição inicial está livre
        self._ensure_initial_not_blocked()

    def _ensure_initial_not_blocked(self):
        """Garante que a posição inicial (0,0) não está bloqueada por obstáculos."""

        y, x = 0, 0
        neighbors = []
        if y < self.height - 1:
            neighbors.append((y+1, x))
        if x < self.width - 1:
            neighbors.append((y, x+1))
        # Se todos os vizinhos são obstáculos, libera um aleatório
        blocked = [self.obstacles[ny][nx] for ny, nx in neighbors]
        if all(blocked):
            idx = random.choice(range(len(neighbors)))
            ny, nx = neighbors[idx]
            self.obstacles[ny][nx] = False

    def get_local_percept(self):
        """
        Retorna:
            Dict contendo sujeira atual e movimentos possíveis
        """

        y, x = self.agent_pos
        percept = {
            'current_dirty': self.grid[y][x],
            'possible_moves': self._get_possible_moves()
        }
        return percept

    def _get_possible_moves(self):
        """
        Calcula os movimentos possíveis a partir da posição atual.
        
        Retorna:
            Lista de movimentos válidos (UP, DOWN, LEFT, RIGHT)
        """

        y, x = self.agent_pos
        moves = []
        # Verifica se o destino não é obstáculo antes de permitir o movimento
        if y > 0 and not self.obstacles[y-1][x]: moves.append('UP')
        if y < self.height - 1 and not self.obstacles[y+1][x]: moves.append('DOWN')
        if x > 0 and not self.obstacles[y][x-1]: moves.append('LEFT')
        if x < self.width - 1 and not self.obstacles[y][x+1]: moves.append('RIGHT')
        return moves

    def execute_action(self, action):
        """
        Executa a ação do agente no ambiente.
        
        Args:
            action: Ação a ser executada (CLEAN, UP, DOWN, LEFT, RIGHT)
        """

        y, x = self.agent_pos
        if action == 'CLEAN':
            self.grid[y][x] = False
        elif action == 'UP' and y > 0 and not self.obstacles[y-1][x]:
            self.agent_pos = (y-1, x)
        elif action == 'DOWN' and y < self.height - 1 and not self.obstacles[y+1][x]:
            self.agent_pos = (y+1, x)
        elif action == 'LEFT' and x > 0 and not self.obstacles[y][x-1]:
            self.agent_pos = (y, x-1)
        elif action == 'RIGHT' and x < self.width - 1 and not self.obstacles[y][x+1]:
            self.agent_pos = (y, x+1)

    def is_clean(self):
        """
        Verifica se todo o ambiente está limpo.
        
        Retorna:
            Boolean indicando se todas as células estão limpas
        """

        return all(not cell for row in self.grid for cell in row)

    def is_obstacle(self, y, x):
        """Verifica se há obstáculo na posição especificada."""
        
        return self.obstacles[y][x]

    # Opcional: método para customizar obstáculos externamente
    def set_obstacle(self, y, x, value=True):
        self.obstacles[y][x] = value
