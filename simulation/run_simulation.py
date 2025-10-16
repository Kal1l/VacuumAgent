import random
import tkinter as tk
from environment.grid_environment import GridEnvironment
from agents.reactive_agent import ReactiveAgent
from agents.model_based_agent import ModelBasedAgent
from evaluation.measures import MeasureCleanPerStep, MeasureCleanAndMovePositive

class VacuumSimulatorGUI:
    CELL_SIZE = 40

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacuum Agent Simulator")
        self.width = 4
        self.height = 4
        self.dirt_prob = 0.3
        self.agent_type = tk.StringVar(value='reactive')
        self.running = False
        self.steps = 1000
        self.current_step = 0
        self.started = False
        self.obstacle_prob = 0.15
        self.scenario_var = tk.StringVar(value="Aleatório")
        self.edit_mode = tk.StringVar(value="obstacle")
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
        self.num_simulations = tk.IntVar(value=1)
        self.show_simulations = tk.BooleanVar(value=False)
        self.initial_grid = None
        self.initial_obstacles = None
        self.initial_agent_pos = None

        # Frame principal para layout vertical
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Frame para controles (lado esquerdo)
        controls_frame = tk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky="n")

        # Frame para canvas (matriz), centralizado
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, sticky="n", padx=(80,0))  # Mais padding para centralizar

        # Frame para legenda (lado direito)
        legend_frame = tk.Frame(main_frame)
        legend_frame.grid(row=0, column=1, rowspan=2, sticky="n", padx=(10,0))

        self._build_controls(controls_frame)
        self.canvas = tk.Canvas(canvas_frame, width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
        self.canvas.pack()
        self.legend_frame = legend_frame
        # Legenda visual ao lado da matriz, só será exibida após carregar cenário
        tk.Label(self.legend_frame, text="Legenda:").pack(anchor="nw")
        legend_col = tk.Frame(self.legend_frame)
        legend_col.pack(anchor="nw")
        row1 = tk.Frame(legend_col)
        row1.pack(anchor="nw")
        tk.Canvas(row1, width=20, height=20, bg="white").pack(side="left")
        tk.Label(row1, text="Livre", anchor="w", padx=2).pack(side="left")
        row2 = tk.Frame(legend_col)
        row2.pack(anchor="nw")
        tk.Canvas(row2, width=20, height=20, bg="brown").pack(side="left")
        tk.Label(row2, text="Sujeira", anchor="w", padx=2).pack(side="left")
        row3 = tk.Frame(legend_col)
        row3.pack(anchor="nw")
        tk.Canvas(row3, width=20, height=20, bg="gray").pack(side="left")
        tk.Label(row3, text="Obstáculo", anchor="w", padx=2).pack(side="left")
        row4 = tk.Frame(legend_col)
        row4.pack(anchor="nw")
        tk.Canvas(row4, width=20, height=20, bg="blue").pack(side="left")
        tk.Label(row4, text="Agente", anchor="w", padx=2).pack(side="left")
        tk.Label(self.legend_frame, text="Modo Edição:\nEsq=Obstáculo\nDir=Sujeira").pack(anchor="nw", pady=(8,0))

    def _build_controls(self, parent):
        row = 0
        # Largura e Altura alinhados
        tk.Label(parent, text="Largura:").grid(row=row, column=0, sticky="e")
        self.width_entry = tk.Entry(parent, width=3)
        self.width_entry.insert(0, str(self.width))
        self.width_entry.grid(row=row, column=1, sticky="w")
        tk.Label(parent, text="Altura:").grid(row=row, column=2, sticky="e")
        self.height_entry = tk.Entry(parent, width=3)
        self.height_entry.insert(0, str(self.height))
        self.height_entry.grid(row=row, column=3, sticky="w")
        row += 1

        # Probabilidades alinhadas
        tk.Label(parent, text="Prob. Sujeira:").grid(row=row, column=0, sticky="e")
        self.dirt_entry = tk.Entry(parent, width=4)
        self.dirt_entry.insert(0, str(self.dirt_prob))
        self.dirt_entry.grid(row=row, column=1, sticky="w")
        tk.Label(parent, text="Prob. Obstáculo:").grid(row=row, column=2, sticky="e")
        self.obstacle_entry = tk.Entry(parent, width=4)
        self.obstacle_entry.insert(0, str(self.obstacle_prob))
        self.obstacle_entry.grid(row=row, column=3, sticky="w")
        row += 1

        # Nº de simulações e botão centralizado
        tk.Label(parent, text="Simulações:").grid(row=row, column=0, sticky="e")
        self.sim_entry = tk.Entry(parent, width=4, textvariable=self.num_simulations)
        self.sim_entry.grid(row=row, column=1, sticky="w")
        tk.Button(parent, text="Simular N", command=self.run_multiple_simulations).grid(row=row, column=2, columnspan=2, sticky="ew")
        row += 1

        tk.Label(parent, text="Agente:").grid(row=row, column=0, sticky="w")
        tk.Radiobutton(parent, text="Reativo", variable=self.agent_type, value='reactive').grid(row=row, column=1, sticky="w")
        tk.Radiobutton(parent, text="Modelo", variable=self.agent_type, value='model').grid(row=row, column=2, sticky="w")
        row += 1

        # Cenário alinhado com criar ambiente e redefinir cenário ao lado
        tk.Label(parent, text="Cenário:").grid(row=row, column=0, sticky="w")
        scenario_menu = tk.OptionMenu(parent, self.scenario_var, *self.scenarios.keys(), command=self.on_scenario_change)
        scenario_menu.grid(row=row, column=1, sticky="w")
        tk.Button(parent, text="Criar", command=self.create_env).grid(row=row, column=2, sticky="ew")
        tk.Button(parent, text="Redefinir", command=self.reset_scenario).grid(row=row, column=3, sticky="ew")
        row += 1

        # Botões iniciar, avançar 1 passo e parar alinhados exatamente abaixo da linha de cenário/criar/redefinir
        tk.Button(parent, text="Iniciar", command=self.start_simulation).grid(row=row, column=0, sticky="ew")
        tk.Button(parent, text="Avançar 1 Passo", command=self.step_once).grid(row=row, column=1, sticky="ew")
        tk.Button(parent, text="Parar", command=self.stop_simulation).grid(row=row, column=2, sticky="ew")
        tk.Label(parent, text="").grid(row=row, column=3)  # Espaço vazio para alinhar com redefinir cenário acima
        row += 1

        self.status_label = tk.Label(parent, text="")
        self.status_label.grid(row=row, column=0, columnspan=4, sticky="w", padx=(5,2), pady=(2,2))

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
        elif scenario is not None:
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
            for (y, x) in scenario.get("dirt", []):
                if 0 <= y < self.height and 0 <= x < self.width:
                    self.env.grid[y][x] = True
            # Aplica obstáculos
            for (y, x) in scenario.get("obstacles", []):
                if 0 <= y < self.height and 0 <= x < self.width:
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
            # Corrigido: use toggle_custom para edição, não toggle_obstacle
            self.canvas.bind("<Button-1>", self.toggle_custom)
            self.canvas.bind("<Button-3>", self.toggle_custom)
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
        if self.scenario_var.get() == "Aleatório":
            self.env = GridEnvironment(self.width, self.height, self.dirt_prob, obstacle_prob=self.obstacle_prob)
            # Salva o estado inicial do ambiente para redefinir depois
            self.initial_grid = [row[:] for row in self.env.grid]
            self.initial_obstacles = [row[:] for row in self.env.obstacles]
            self.initial_agent_pos = self.env.agent_pos
            self.canvas.config(width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
            self.agent = None
            self.measure1 = None
            self.measure2 = None
            self.running = False
            self.current_step = 0
            self.started = False
            self.draw_grid()
            self.status_label.config(text="Ambiente criado.")
            # Corrigido: use toggle_custom para edição de obstáculos/sujeira
            self.canvas.bind("<Button-1>", self.toggle_custom)
            self.canvas.bind("<Button-3>", self.toggle_custom)
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
        self.measure2 = MeasureCleanAndMovePositive()
        self.current_step = 0
        self.started = False
        self.penalty_score = 0  # inicializa penalidade
        self.simulation_step(self.current_step)

    def stop_simulation(self):
        self.running = False

    def simulation_step(self, step):
        # Corrige parada: só para se já saiu da posição inicial e voltou
        if not self.running or step >= self.steps or (self.started and self.env.agent_pos == (0, 0)):
            final_status = f"Fim! Passos: {step} | Limpo: {self.measure1.score} | Limpo/Penalidade: {self.penalty_score} |  Chegou à posição final: {'Sim' if self.env.agent_pos == (0, 0) else 'Não'}"
            self.status_label.config(text=final_status)
            return
        # Atualize a quantidade de passos em tempo real
        self.status_label.config(
            text=f"Passos: {step} | Limpo: {self.measure1.score} | Limpo/Penalidade: {self.penalty_score}"
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
        moved = action in ['UP', 'DOWN', 'LEFT', 'RIGHT']
        self.measure1.update(cleaned)
        self.measure2.update(cleaned, moved)
        # Penalidade: +1 por movimento, -1 por limpar
        if cleaned:
            self.penalty_score -= 1
        if moved:
            self.penalty_score += 1
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
            self.measure2 = MeasureCleanAndMovePositive()
            self.current_step = 0
            self.started = False  # reset ao iniciar
            self.penalty_score = 0  # inicializa penalidade
        # Corrige parada: só para se já saiu da posição inicial e voltou
        if self.started and self.env.agent_pos == (0, 0):
            final_status = f"Fim! Limpo: {self.measure1.score}, Limpo/Penalidade: {self.penalty_score}, Passos: {self.current_step} | Sujeiras limpas: {self.measure2.cleaned} | Chegou à posição final: {'Sim' if self.env.agent_pos == (0, 0) else 'Não'}"
            self.status_label.config(text=final_status)
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
        moved = action in ['UP', 'DOWN', 'LEFT', 'RIGHT']
        self.measure1.update(cleaned)
        self.measure2.update(cleaned, moved)
        # Penalidade: +1 por movimento, -1 por limpar
        if cleaned:
            self.penalty_score -= 1
        if moved:
            self.penalty_score += 1
        self.draw_grid(highlight)
        self.current_step += 1
        if self.env.agent_pos != (0, 0):
            self.started = True
        self.status_label.config(
            text=f"Passos: {self.current_step} | Limpo: {self.measure1.score} | Limpo/Penalidade: {self.penalty_score}"
        )
        if highlight:
            self.root.after(300, lambda: self.draw_grid())

    def run_multiple_simulations(self):
        try:
            n = int(self.sim_entry.get())
        except ValueError:
            self.status_label.config(text="Número de simulações inválido!")
            return
        if not self.env:
            self.status_label.config(text="Crie o ambiente primeiro.")
            return

        initial_grid = [row[:] for row in self.env.grid]
        initial_obstacles = [row[:] for row in self.env.obstacles]
        initial_agent_pos = self.env.agent_pos

        stats = {'penalty': [], 'steps': [], 'cleaned': [], 'final': [], 'all_cleaned': []}
        agent_type = self.agent_type.get()
        total_penalty = 0  # Soma das penalidades de todas as simulações
        for i in range(n):
            self.env.grid = [row[:] for row in initial_grid]
            self.env.obstacles = [row[:] for row in initial_obstacles]
            self.env.agent_pos = initial_agent_pos
            if agent_type == 'reactive':
                agent = ReactiveAgent()
            else:
                agent = ModelBasedAgent()
                agent.pos = self.env.agent_pos
            cleaned_count = 0
            penalty_score = 0
            current_step = 0
            started = False
            max_steps = self.steps
            while current_step < max_steps:
                percept = self.env.get_local_percept()
                action = agent.select_action(percept)
                prev_pos = self.env.agent_pos
                self.env.execute_action(action)
                if hasattr(agent, 'pos'):
                    agent.pos = self.env.agent_pos
                cleaned = action == 'CLEAN'
                if cleaned:
                    cleaned_count += 1
                    penalty_score -= 1  # penalidade diminui ao limpar
                if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    penalty_score += 1  # penalidade aumenta a cada movimento
                current_step += 1
                if self.env.agent_pos != (0, 0):
                    started = True
                self.draw_grid()
                self.status_label.config(
                    text=f"Simulação {i+1}/{n} | Passos: {current_step} | Limpo: {cleaned_count} | Penalidade: {penalty_score}"
                )
                self.root.update()
                self.root.after(30)
                if started and self.env.agent_pos == (0, 0):
                    break
            total_penalty += penalty_score
            stats['penalty'].append(penalty_score)
            stats['steps'].append(current_step)
            stats['cleaned'].append(cleaned_count)
            stats['final'].append(1 if self.env.agent_pos == (0, 0) else 0)
            stats['all_cleaned'].append(1 if self.env.is_clean() else 0)

        def avg(lst): return sum(lst)/len(lst) if lst else 0
        def pct(lst): return 100*sum(lst)/len(lst) if lst else 0

        msg = f"Resultados após {n} simulações ({'Reativo' if agent_type=='reactive' else 'Modelo'}):\n"
        msg += f"  Média penalidade: {avg(stats['penalty']):.2f}\n"
        msg += f"  Soma das penalidades: {total_penalty}\n"
        msg += f"  Média passos: {avg(stats['steps']):.2f}\n"
        msg += f"  Média sujeiras limpas: {avg(stats['cleaned']):.2f}\n"
        msg += f"  % chegou ao final: {pct(stats['final']):.1f}%\n"
        msg += f"  % limpou tudo: {pct(stats['all_cleaned']):.1f}%\n"

        self.status_label.config(text=msg)

    def _get_target_pos(self, pos, action):
        y, x = pos
        if action == 'UP': return (y-1, x)
        if action == 'DOWN': return (y+1, x)
        if action == 'LEFT': return (y, x-1)
        if action == 'RIGHT': return (y, x+1)
        return pos

    def draw_grid(self, highlight=None):
        self.canvas.delete("all")
        if not hasattr(self, 'env') or self.env is None:
            return
        for y in range(self.height):
            for x in range(self.width):
                cell_x = x * self.CELL_SIZE
                cell_y = y * self.CELL_SIZE
                if highlight == (y, x):
                    color = "red"
                elif self.env.is_obstacle(y, x):
                    color = "gray"
                elif self.env.grid[y][x]:
                    color = "brown"
                else:
                    color = "white"
                self.canvas.create_rectangle(cell_x, cell_y, cell_x+self.CELL_SIZE, cell_y+self.CELL_SIZE, fill=color, outline="black")
        ay, ax = self.env.agent_pos
        self.canvas.create_oval(
            ax*self.CELL_SIZE+5, ay*self.CELL_SIZE+5,
            ax*self.CELL_SIZE+self.CELL_SIZE-5, ay*self.CELL_SIZE+self.CELL_SIZE-5,
            fill="blue"
        )

    def reset_scenario(self):
        # Restaura o ambiente ao estado inicial salvo
        if self.initial_grid is not None and self.initial_obstacles is not None and self.initial_agent_pos is not None:
            self.env.grid = [row[:] for row in self.initial_grid]
            self.env.obstacles = [row[:] for row in self.initial_obstacles]
            self.env.agent_pos = self.initial_agent_pos
            self.agent = None
            self.measure1 = None
            self.measure2 = None
            self.running = False
            self.current_step = 0
            self.started = False
            self.penalty_score = 0
            self.draw_grid()
            self.status_label.config(text="Cenário redefinido.")
        else:
            # Se não há estado salvo, recarrega como antes
            scenario_name = self.scenario_var.get()
            if scenario_name in self.scenarios:
                self.load_scenario(scenario_name)
            else:
                self.create_env()
            self.agent = None
            self.measure1 = None
            self.measure2 = None
            self.running = False
            self.current_step = 0
            self.started = False
            self.penalty_score = 0
            self.status_label.config(text="Cenário redefinido.")

def main():
    gui = VacuumSimulatorGUI()
    gui.root.mainloop()

if __name__ == "__main__":
    main()
