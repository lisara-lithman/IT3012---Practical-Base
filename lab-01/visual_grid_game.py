iimport random, tkinter as tk

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
    """A Model-Based Agent using memory & transition state to explore systematically."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.visited = {(0, 0)}
        self.last_action = 'Up'

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update Transition Model (position history)
        if self.last_action == 'Up': self.y += 1
        elif self.last_action == 'Down': self.y -= 1
        elif self.last_action == 'Left': self.x -= 1
        elif self.last_action == 'Right': self.x += 1

        self.visited.add((self.x, self.y))

        # Rule 1: Priority - Eat food
        if percept.get('food_here'):
            return 'Stay'

        # Candidate directions and their target relative coordinates
        neighbors = {
            'Up': (self.x, self.y + 1),
            'Right': (self.x + 1, self.y),
            'Down': (self.x, self.y - 1),
            'Left': (self.x - 1, self.y)
        }

        # If wall_ahead is True, continuing straight is blocked
        blocked_action = self.last_action if percept.get('wall_ahead') else None

        # Rule 2: Keep going straight if unvisited and clear
        if self.last_action != blocked_action and neighbors[self.last_action] not in self.visited:
            action = self.last_action
        else:
            # Rule 3: Otherwise, select the first available unvisited direction
            unvisited = [act for act, pos in neighbors.items() 
                         if act != blocked_action and pos not in self.visited]
            
            if unvisited:
                action = unvisited[0]
            else:
                # Rule 4: Loop escape - pick any valid path that avoids immediately backtracking
                opposite = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
                valid = [act for act in ['Up', 'Right', 'Down', 'Left'] if act != blocked_action]
                non_backtrack = [act for act in valid if act != opposite.get(self.last_action)]
                action = non_backtrack[0] if non_backtrack else valid[0]

        self.last_action = action
        return action


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