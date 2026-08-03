import random, tkinter as tk

class VisualGridHuntGame:
    def __init__(self, width=12, height=12, num_food=15, num_opponents=0, num_traps=5, custom_walls=None):
        self.width, self.height = width, height
        self.agent_pos = [0, 0]
        self.facing = 'Up'
        self.walls = set(custom_walls) if custom_walls else {(2,2), (2,3), (5,5), (6,5), (3,7)}
        
        self.food_positions, self.toxic_traps, self.opponents = set(), set(), []
        while len(self.food_positions) < num_food:
            p = (random.randint(0, width-1), random.randint(0, height-1))
            if p != (0,0) and p not in self.walls: self.food_positions.add(p)
            
        while len(self.toxic_traps) < num_traps:
            p = (random.randint(0, width-1), random.randint(0, height-1))
            if p != (0,0) and p not in self.walls and p not in self.food_positions: self.toxic_traps.add(p)

        self.score, self.steps, self.collision = 0, 0, False

    def get_percept(self) -> dict:
        x, y = self.agent_pos
        front_map = {'Up': (x, y+1), 'Down': (x, y-1), 'Left': (x-1, y), 'Right': (x+1, y)}
        front_cell = front_map[self.facing]

        wall_ahead = (front_cell in self.walls or front_cell[0] < 0 or front_cell[0] >= self.width 
                      or front_cell[1] < 0 or front_cell[1] >= self.height)
        food_here = tuple(self.agent_pos) in self.food_positions

        return {'wall_ahead': wall_ahead, 'food_here': food_here, 
                'hit_wall': tuple(self.agent_pos) in self.walls, 'collision': self.collision, 'score': self.score}

    def execute_action(self, action: str):
        self.steps += 1
        if action in ['Up', 'Down', 'Left', 'Right']:
            self.facing = action  # Update environment facing direction

        new_pos = list(self.agent_pos)
        if action == 'Up': new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down': new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left': new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right': new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls: self.score -= 5
        else: self.agent_pos = new_pos

        pos = tuple(self.agent_pos)
        if pos in self.food_positions:
            self.food_positions.remove(pos); self.score += 20
        if pos in self.toxic_traps: self.score -= 15

    def is_done(self):
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'): return 'Stay'
        if percept.get('wall_ahead'): return 'Right'
        return 'Up'


class ModelBasedAgent:
    """Step 2: Model-Based Agent with internal state, coordinate tracking, and memory."""

    def __init__(self):
        # 1. Internal State / Transition Model
        self.x = 0
        self.y = 0
        self.facing = 'Up'
        
        # 2. Memory Stores
        self.visited = {(0, 0)}
        self.known_walls = set()
        self.last_action = None

    def _get_offset(self, action: str) -> tuple:
        offsets = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        return offsets.get(action, (0, 0))

    def sense_and_act(self, percept: dict) -> str:
        # ------------------------------------------------------------------
        # A. UPDATE INTERNAL STATE (Transition Model)
        # ------------------------------------------------------------------
        if self.last_action and self.last_action != 'Stay':
            self.facing = self.last_action
            
            # If we didn't hit a wall in the last turn, update coordinates
            dx, dy = self._get_offset(self.last_action)
            self.x += dx
            self.y += dy
            self.visited.add((self.x, self.y))

        # Record wall position ahead if detected
        if percept.get('wall_ahead'):
            dx, dy = self._get_offset(self.facing)
            self.known_walls.add((self.x + dx, self.y + dy))

        # ------------------------------------------------------------------
        # B. CONDITION-ACTION RULES (Querying Memory)
        # ------------------------------------------------------------------
        
        # Rule 1: Priority - Eat food if present
        if percept.get('food_here'):
            self.last_action = 'Stay'
            return 'Stay'

        # Calculate coordinates of adjacent cells
        neighbor_map = {
            'Up': (self.x, self.y + 1),
            'Right': (self.x + 1, self.y),
            'Down': (self.x, self.y - 1),
            'Left': (self.x - 1, self.y)
        }

        # Filter out actions that lead into known walls
        valid_actions = []
        for act, target_pos in neighbor_map.items():
            if target_pos in self.known_walls:
                continue
            if act == self.facing and percept.get('wall_ahead'):
                continue
            valid_actions.append(act)

        if not valid_actions:
            valid_actions = ['Up', 'Right', 'Down', 'Left']  # Fallback

        # Rule 2: Prefer moves to UNVISITED cells (Exploration)
        unvisited_actions = [
            act for act in valid_actions if neighbor_map[act] not in self.visited
        ]

        if unvisited_actions:
            # If moving forward is unvisited, maintain momentum
            if self.facing in unvisited_actions:
                chosen_action = self.facing
            else:
                chosen_action = unvisited_actions[0]
        else:
            # Rule 3: Loop Escape / Backtracking (All neighbors visited)
            # Pick a valid non-wall direction to backtrack out of the loop
            chosen_action = valid_actions[0]

        self.last_action = chosen_action
        return chosen_action


class GridGameGUI:
    def __init__(self, root, width=12, height=12, num_food=15, num_opponents=0, num_traps=5):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")
        self.env = VisualGridHuntGame(width, height, num_food, num_opponents, num_traps)
        
        self.cell_size = max(20, min(600 // self.env.width, 600 // self.env.height))
        self.canvas = tk.Canvas(root, width=self.env.width*self.cell_size, height=self.env.height*self.cell_size, bg="white")
        self.canvas.pack()
        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)
        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop)
        self.btn.pack(pady=5)
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        cs = self.cell_size
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1, y1 = x * cs, (self.env.height - 1 - y) * cs
                color = "#64748b" if (x,y) in self.env.walls else "#f1f5f9"
                self.canvas.create_rectangle(x1, y1, x1+cs, y1+cs, fill=color, outline="#cbd5e1")

        for fx, fy in self.env.food_positions:
            x1, y1 = fx*cs + cs*0.25, (self.env.height-1-fy)*cs + cs*0.25
            self.canvas.create_oval(x1, y1, x1+cs*0.5, y1+cs*0.5, fill="#f59e0b")

        for tx, ty in self.env.toxic_traps:
            x1, y1 = tx*cs + cs*0.25, (self.env.height-1-ty)*cs + cs*0.25
            self.canvas.create_polygon(x1+cs*0.25, y1, x1+cs*0.5, y1+cs*0.5, x1+cs*0.25, y1+cs, x1, y1+cs*0.5, fill="purple")

        ax, ay = self.env.agent_pos
        x1, y1 = ax*cs + cs*0.15, (self.env.height-1-ay)*cs + cs*0.15
        self.canvas.create_oval(x1, y1, x1+cs*0.7, y1+cs*0.7, fill="#000066")

    def run_loop(self):
        self.btn.config(state="disabled")
        agent = ModelBasedAgent()

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = agent.sense_and_act(percept)
                self.env.execute_action(action)
                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                self.label.config(text=f"Finished! Final Score: {self.env.score}")
                self.btn.config(state="normal")
        step()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridGameGUI(root)
    root.mainloop()