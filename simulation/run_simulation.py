import random
import tkinter as tk
from environment.grid_environment import GridEnvironment
from agents.reactive_agent import ReactiveAgent
from agents.model_based_agent import ModelBasedAgent
from evaluation.measures import MeasureCleanPerStep, MeasureCleanAndMovePenalty

class VacuumSimulatorGUI:
    CELL_SIZE = 40

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacuum Agent Simulator")
        self.width = 4  # tamanho default 4x4
        self.height = 4
        self.dirt_prob = 0.3
        self.agent_type = tk.StringVar(value='reactive')
        self.running = False
        self.steps = 1000 #Quantidade Maxima de passos
        self.current_step = 0  # para controle do passo único
        self.started = False  # novo atributo para controlar início
        self.obstacle_prob = 0.15  # valor default
        self.scenario_var = tk.StringVar(value="Aleatório")
        self.edit_mode = tk.StringVar(value="obstacle")  # "obstacle" ou "dirt"
        self.custom_dirt = set()
        self.custom_obstacles = set()
        self.scenarios = {
            "Aleatório": None,
            "Custom": {
                "width": 4, "height": 4,
                "dirt": [],
                "obstacles": []
            },
            "Cenário 1": {
                "width": 5, "height": 5,
                "dirt": [(0,0), (1,2), (2,2), (4,4)],
                "obstacles": [(1,1), (2,1), (3,3)]
            },
            "Cenário 2": {
                "width": 6, "height": 4,
                "dirt": [(0,3), (1,0), (2,2), (3,5)],
                "obstacles": [(0,2), (1,4), (3,1), (3,2)]
            },
            "Cenário 3": {
                "width": 4, "height": 4,
                "dirt": [(0,1), (1,2), (2,3), (3,0)],
                "obstacles": []
            }
        }

        self._build_controls()
        self.canvas = tk.Canvas(self.root, width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
        self.canvas.grid(row=1, column=0, columnspan=6, sticky="w", padx=(5,0), pady=(5,0))
        # Legenda visual ao lado da matriz, só será exibida após carregar cenário
        self.legend_frame = tk.Frame(self.root)
        self.legend_frame.grid(row=1, column=self.height+1, sticky="nw", padx=(0,5), pady=(5,0))
        self.legend_frame.grid_remove()  # Oculta inicialmente
        tk.Label(self.legend_frame, text="Legenda:").pack(anchor="w")
        legend_row = tk.Frame(self.legend_frame)
        legend_row.pack(anchor="w")
        tk.Canvas(legend_row, width=20, height=20, bg="white").pack(side="left", padx=(0,2))
        tk.Label(legend_row, text="Livre", anchor="w", padx=2).pack(side="left")
        tk.Canvas(legend_row, width=20, height=20, bg="brown").pack(side="left", padx=(0,2))
        tk.Label(legend_row, text="Sujeira", anchor="w", padx=2).pack(side="left")
        tk.Canvas(legend_row, width=20, height=20, bg="gray").pack(side="left", padx=(0,2))
        tk.Label(legend_row, text="Obstáculo", anchor="w", padx=2).pack(side="left")
        tk.Canvas(legend_row, width=20, height=20, bg="blue").pack(side="left", padx=(0,2))
        tk.Label(legend_row, text="Agente", anchor="w", padx=2).pack(side="left")
        tk.Label(self.legend_frame, text="Modo Edição: Esq=Obstáculo, Dir=Sujeira").pack(anchor="w", pady=(8,0))
        # ...existing code...

    def _build_controls(self):
        # Barra superior mais compacta
        tk.Label(self.root, text="Largura:").grid(row=0, column=0, sticky="w", padx=(5,2), pady=(5,2))
        self.width_entry = tk.Entry(self.root, width=3)
        self.width_entry.insert(0, str(self.width))
        self.width_entry.grid(row=0, column=1, sticky="w", padx=(0,2), pady=(5,2))

        tk.Label(self.root, text="Altura:").grid(row=0, column=2, sticky="w", padx=(0,2), pady=(5,2))
        self.height_entry = tk.Entry(self.root, width=3)
        self.height_entry.insert(0, str(self.height))
        self.height_entry.grid(row=0, column=3, sticky="w", padx=(0,2), pady=(5,2))

        tk.Label(self.root, text="Prob. Sujeira:").grid(row=0, column=4, sticky="w", padx=(0,2), pady=(5,2))
        self.dirt_entry = tk.Entry(self.root, width=4)
        self.dirt_entry.insert(0, str(self.dirt_prob))
        self.dirt_entry.grid(row=0, column=5, sticky="w", padx=(0,2), pady=(5,2))

        tk.Label(self.root, text="Prob. Obstáculo:").grid(row=0, column=6, sticky="w", padx=(0,2), pady=(5,2))
        self.obstacle_entry = tk.Entry(self.root, width=4)
        self.obstacle_entry.insert(0, str(self.obstacle_prob))
        self.obstacle_entry.grid(row=0, column=7, sticky="w", padx=(0,2), pady=(5,2))

        tk.Label(self.root, text="Agente:").grid(row=2, column=0, sticky="w", padx=(5,2), pady=(2,2))
        tk.Radiobutton(self.root, text="Reativo", variable=self.agent_type, value='reactive').grid(row=2, column=1, sticky="w", padx=(0,2), pady=(2,2))
        tk.Radiobutton(self.root, text="Modelo", variable=self.agent_type, value='model').grid(row=2, column=2, sticky="w", padx=(0,2), pady=(2,2))

        tk.Button(self.root, text="Criar Ambiente", command=self.create_env).grid(row=2, column=3, sticky="w", padx=(0,2), pady=(2,2))
        tk.Button(self.root, text="Iniciar", command=self.start_simulation).grid(row=2, column=4, sticky="w", padx=(0,2), pady=(2,2))
        tk.Button(self.root, text="Parar", command=self.stop_simulation).grid(row=2, column=5, sticky="w", padx=(0,2), pady=(2,2))
        tk.Button(self.root, text="Avançar 1 Passo", command=self.step_once).grid(row=2, column=6, sticky="w", padx=(0,2), pady=(2,2))

        tk.Label(self.root, text="Cenário:").grid(row=0, column=8, sticky="w", padx=(0,2), pady=(5,2))
        scenario_menu = tk.OptionMenu(self.root, self.scenario_var, *self.scenarios.keys(), command=self.on_scenario_change)
        scenario_menu.grid(row=0, column=9, sticky="w", padx=(0,2), pady=(5,2))

        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=3, column=0, columnspan=7, sticky="w", padx=(5,2), pady=(2,2))

    def on_scenario_change(self, value):
        self.load_scenario(value)

    def load_scenario(self, scenario_name):
        scenario = self.scenarios.get(scenario_name)
        if scenario_name == "Custom":
            self.width = scenario["width"]
            self.height = scenario["height"]
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.height))
            self.dirt_prob = 0.0
            self.dirt_entry.delete(0, tk.END)
            self.dirt_entry.insert(0, str(self.dirt_prob))
            self.obstacle_prob = 0.0
            self.obstacle_entry.delete(0, tk.END)
            self.obstacle_entry.insert(0, str(self.obstacle_prob))
            self.env = GridEnvironment(self.width, self.height, dirt_prob=0.0, obstacle_prob=0.0)
            for y in range(self.height):
                for x in range(self.width):
                    self.env.grid[y][x] = False
                    self.env.obstacles[y][x] = False
            self.custom_dirt = set()
            self.custom_obstacles = set()
            self.canvas.config(width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
            self.agent = None
            self.measure1 = None
            self.measure2 = None
            self.running = False
            self.current_step = 0
            self.started = False
            self.draw_grid()
            self.status_label.config(text="Modo Custom: clique para editar obstáculos/sujeira.")
            self.canvas.bind("<Button-1>", self.toggle_custom)
            self.canvas.bind("<Button-3>", self.toggle_custom)
        elif scenario:
            self.width = scenario["width"]
            self.height = scenario["height"]
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.height))
            self.dirt_prob = 0.0
            self.dirt_entry.delete(0, tk.END)
            self.dirt_entry.insert(0, str(self.dirt_prob))
            self.obstacle_prob = 0.0
            self.obstacle_entry.delete(0, tk.END)
            self.obstacle_entry.insert(0, str(self.obstacle_prob))
            self.env = GridEnvironment(self.width, self.height, dirt_prob=0.0, obstacle_prob=0.0)
            # Limpa grid
            for y in range(self.height):
                for x in range(self.width):
                    self.env.grid[y][x] = False
                    self.env.obstacles[y][x] = False
            # Aplica sujeira
            for (y, x) in scenario["dirt"]:
                self.env.grid[y][x] = True
            # Aplica obstáculos
            for (y, x) in scenario["obstacles"]:
                self.env.obstacles[y][x] = True
            self.canvas.config(width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
            self.agent = None
            self.measure1 = None
            self.measure2 = None
            self.running = False
            self.current_step = 0
            self.started = False
            self.draw_grid()
            self.status_label.config(text=f"{scenario_name} carregado.")
            self.canvas.bind("<Button-1>", self.toggle_obstacle)
        else:
            self.create_env()
        # Exibe legenda ao carregar qualquer cenário
        self.legend_frame.grid()  # Torna visível

    def create_env(self):
        try:
            self.width = int(self.width_entry.get())
            self.height = int(self.height_entry.get())
            self.dirt_prob = float(self.dirt_entry.get())
            self.obstacle_prob = float(self.obstacle_entry.get())
        except ValueError:
            self.status_label.config(text="Valores inválidos!")
            return
        # Adiciona probabilidade de obstáculos (fixo ou pode adicionar campo na interface)
        # Se cenário for "Aleatório", cria ambiente normalmente
        if self.scenario_var.get() == "Aleatório":
            self.env = GridEnvironment(self.width, self.height, self.dirt_prob, obstacle_prob=self.obstacle_prob)
            self.canvas.config(width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
            self.agent = None
            self.measure1 = None
            self.measure2 = None
            self.running = False
            self.current_step = 0
            self.started = False
            self.draw_grid()
            self.status_label.config(text="Ambiente criado.")
            self.canvas.bind("<Button-1>", self.toggle_obstacle)
        elif self.scenario_var.get() == "Custom":
            self.load_scenario("Custom")
        else:
            self.load_scenario(self.scenario_var.get())
        self.legend_frame.grid()  # Torna visível ao criar ambiente

    def toggle_custom(self, event):
        x = event.x // self.CELL_SIZE
        y = event.y // self.CELL_SIZE
        if 0 <= x < self.width and 0 <= y < self.height:
            if (y, x) == (0, 0):
                return
            if event.num == 1:  # Botão esquerdo: obstáculo
                # Se há sujeira, remova a sujeira antes de adicionar obstáculo
                if self.env.grid[y][x]:
                    self.env.grid[y][x] = False
                    self.custom_dirt.discard((y, x))
                current = self.env.is_obstacle(y, x)
                self.env.set_obstacle(y, x, not current)
                if not current:
                    self.custom_obstacles.add((y, x))
                else:
                    self.custom_obstacles.discard((y, x))
            elif event.num == 3:  # Botão direito: sujeira
                # Se há obstáculo, remova o obstáculo antes de adicionar sujeira
                if self.env.is_obstacle(y, x):
                    self.env.set_obstacle(y, x, False)
                    self.custom_obstacles.discard((y, x))
                current = self.env.grid[y][x]
                self.env.grid[y][x] = not current
                if not current:
                    self.custom_dirt.add((y, x))
                else:
                    self.custom_dirt.discard((y, x))
            self.draw_grid()

    def start_simulation(self):
        if not self.env:
            self.status_label.config(text="Crie o ambiente primeiro.")
            return
        self.running = True
        if self.agent_type.get() == 'reactive':
            self.agent = ReactiveAgent()
        else:
            self.agent = ModelBasedAgent()
            self.agent.pos = self.env.agent_pos
        self.measure1 = MeasureCleanPerStep()
        self.measure2 = MeasureCleanAndMovePenalty()
        self.current_step = 0
        self.started = False
        self.simulation_step(self.current_step)

    def stop_simulation(self):
        self.running = False

    def simulation_step(self, step):
        # Corrige parada: só para se já saiu da posição inicial e voltou
        if not self.running or step >= self.steps or (self.started and self.env.agent_pos == (0, 0)):
            self.status_label.config(
                text=f"Fim!  Passos: {step} | Limpo: {self.measure1.score}| Limpo/Penalidade: {self.measure2.score}"
            )
            return
        # Atualize a quantidade de passos em tempo real
        self.status_label.config(
            text=f"Passos: {step} | Limpo: {self.measure1.score} | Limpo/Penalidade: {self.measure2.score}"
        )
        percept = self.env.get_local_percept()
        action = self.agent.select_action(percept)
        prev_pos = self.env.agent_pos

        # Indicação visual para tentativa de movimento inválido (reativo)
        highlight = None
        if self.agent_type.get() == 'reactive' and action != 'CLEAN' and action not in percept['possible_moves']:
            target_pos = self._get_target_pos(prev_pos, action)
            highlight = target_pos

        # Executa ação normalmente
        self.env.execute_action(action)
        if hasattr(self.agent, 'pos'):
            self.agent.pos = self.env.agent_pos
        cleaned = action == 'CLEAN'
        moved = self.env.agent_pos != prev_pos
        self.measure1.update(cleaned)
        self.measure2.update(cleaned, moved)
        self.draw_grid(highlight)
        self.current_step = step + 1
        if self.env.agent_pos != (0, 0):
            self.started = True
        if highlight:
            # Remove destaque após 300ms
            self.root.after(300, lambda: self.draw_grid())
            self.root.after(300, lambda: self.simulation_step(self.current_step))
        else:
            self.root.after(300, lambda: self.simulation_step(self.current_step))

    def step_once(self):
        # Executa apenas um passo da simulação
        if not self.env:
            self.status_label.config(text="Crie o ambiente primeiro.")
            return
        if self.agent is None:
            if self.agent_type.get() == 'reactive':
                self.agent = ReactiveAgent()
            else:
                self.agent = ModelBasedAgent()
                self.agent.pos = self.env.agent_pos
            self.measure1 = MeasureCleanPerStep()
            self.measure2 = MeasureCleanAndMovePenalty()
            self.current_step = 0
            self.started = False  # reset ao iniciar
        # Corrige parada: só para se já saiu da posição inicial e voltou
        if self.started and self.env.agent_pos == (0, 0):
            self.status_label.config(
                text=f"Fim! Limpo: {self.measure1.score}, Limpo/Penalidade: {self.measure2.score}, Passos: {self.current_step}"
            )
            return
        percept = self.env.get_local_percept()
        action = self.agent.select_action(percept)
        prev_pos = self.env.agent_pos

        highlight = None
        if self.agent_type.get() == 'reactive' and action != 'CLEAN' and action not in percept['possible_moves']:
            target_pos = self._get_target_pos(prev_pos, action)
            highlight = target_pos

        self.env.execute_action(action)
        if hasattr(self.agent, 'pos'):
            self.agent.pos = self.env.agent_pos
        cleaned = action == 'CLEAN'
        moved = self.env.agent_pos != prev_pos
        self.measure1.update(cleaned)
        self.measure2.update(cleaned, moved)
        self.draw_grid(highlight)
        self.current_step += 1
        if self.env.agent_pos != (0, 0):
            self.started = True
        self.status_label.config(
            text=f"Passos: {self.current_step} | Limpo: {self.measure1.score} | Limpo/Penalidade: {self.measure2.score}"
        )
        if highlight:
            self.root.after(300, lambda: self.draw_grid())

    def _get_target_pos(self, pos, action):
        y, x = pos
        if action == 'UP': return (y-1, x)
        if action == 'DOWN': return (y+1, x)
        if action == 'LEFT': return (y, x-1)
        if action == 'RIGHT': return (y, x+1)
        return pos

    def draw_grid(self, highlight=None):
        self.canvas.delete("all")
        for y in range(self.height):
            for x in range(self.width):
                cell_x = x * self.CELL_SIZE
                cell_y = y * self.CELL_SIZE
                if highlight == (y, x):
                    color = "red"
                elif self.env and self.env.is_obstacle(y, x):
                    color = "gray"
                elif self.env and self.env.grid[y][x]:
                    color = "brown"
                else:
                    color = "white"
                self.canvas.create_rectangle(cell_x, cell_y, cell_x+self.CELL_SIZE, cell_y+self.CELL_SIZE, fill=color, outline="black")
        if self.env:
            ay, ax = self.env.agent_pos
            self.canvas.create_oval(
                ax*self.CELL_SIZE+5, ay*self.CELL_SIZE+5,
                ax*self.CELL_SIZE+self.CELL_SIZE-5, ay*self.CELL_SIZE+self.CELL_SIZE-5,
                fill="blue"
            )

def main():
    gui = VacuumSimulatorGUI()
    gui.root.mainloop()

if __name__ == "__main__":
    main()
