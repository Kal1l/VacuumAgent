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

        self._build_controls()
        self.canvas = tk.Canvas(self.root, width=self.width*self.CELL_SIZE, height=self.height*self.CELL_SIZE)
        self.canvas.grid(row=1, column=0, columnspan=7)
        self.env = None
        self.agent = None
        self.measure1 = None
        self.measure2 = None

    def _build_controls(self):
        tk.Label(self.root, text="Largura:").grid(row=0, column=0)
        self.width_entry = tk.Entry(self.root, width=3)
        self.width_entry.insert(0, str(self.width))
        self.width_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Altura:").grid(row=0, column=2)
        self.height_entry = tk.Entry(self.root, width=3)
        self.height_entry.insert(0, str(self.height))
        self.height_entry.grid(row=0, column=3)

        tk.Label(self.root, text="Prob. Sujeira:").grid(row=0, column=4)
        self.dirt_entry = tk.Entry(self.root, width=4)
        self.dirt_entry.insert(0, str(self.dirt_prob))
        self.dirt_entry.grid(row=0, column=5)

        tk.Label(self.root, text="Prob. Obstáculo:").grid(row=0, column=6)
        self.obstacle_entry = tk.Entry(self.root, width=4)
        self.obstacle_entry.insert(0, str(self.obstacle_prob))
        self.obstacle_entry.grid(row=0, column=7)

        tk.Label(self.root, text="Agente:").grid(row=2, column=0)
        tk.Radiobutton(self.root, text="Reativo", variable=self.agent_type, value='reactive').grid(row=2, column=1)
        tk.Radiobutton(self.root, text="Modelo", variable=self.agent_type, value='model').grid(row=2, column=2)

        tk.Button(self.root, text="Criar Ambiente", command=self.create_env).grid(row=2, column=3)
        tk.Button(self.root, text="Iniciar", command=self.start_simulation).grid(row=2, column=4)
        tk.Button(self.root, text="Parar", command=self.stop_simulation).grid(row=2, column=5)
        tk.Button(self.root, text="Avançar 1 Passo", command=self.step_once).grid(row=2, column=6)  # novo botão

        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=3, column=0, columnspan=7)

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
        # Permite clicar para adicionar/remover obstáculos
        self.canvas.bind("<Button-1>", self.toggle_obstacle)

    def toggle_obstacle(self, event):
        # Permite customizar obstáculos clicando na célula
        x = event.x // self.CELL_SIZE
        y = event.y // self.CELL_SIZE
        if 0 <= x < self.width and 0 <= y < self.height:
            # Não permite obstáculo na posição inicial do agente
            if (y, x) != (0, 0):
                current = self.env.is_obstacle(y, x)
                self.env.set_obstacle(y, x, not current)
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
        self.started = False  # reset ao iniciar
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
