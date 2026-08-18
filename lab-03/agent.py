import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            if percept.get('all_food'):
                start = tuple(percept['agent_pos'])
                closest_food = min(
                    percept['all_food'], 
                    key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1])
                )
                
                walls = set(percept.get('walls', []))
                width, height = percept.get('grid_size', (10, 10))
                
                def get_successors(pos):
                    x, y = pos
                    successors = []
                    if y + 1 < height and (x, y + 1) not in walls:
                        successors.append(((x, y + 1), 'Up', 1))
                    if y - 1 >= 0 and (x, y - 1) not in walls:
                        successors.append(((x, y - 1), 'Down', 1))
                    if x - 1 >= 0 and (x - 1, y) not in walls:
                        successors.append(((x - 1, y), 'Left', 1))
                    if x + 1 < width and (x + 1, y) not in walls:
                        successors.append(((x + 1, y), 'Right', 1))
                    return successors

                if self.active_algo == 'BFS':
                    self.plan = self.bfs_search(start, tuple(closest_food), get_successors)
                elif self.active_algo == 'DFS':
                    self.plan = self.dfs_search(start, tuple(closest_food), get_successors)
                elif self.active_algo == 'UCS':
                    self.plan = self.ucs_search(start, tuple(closest_food), get_successors)

        if self.plan:
            return self.plan.pop(0)
        return 'Stay'
    
    def bfs_search(self, start, goal, get_successors):
        frontier = deque()
        frontier.append((start, []))
        reached = set()
        reached.add(start)

        while frontier:
            current, path = frontier.popleft()

            if current == goal:
                return path

            for next_state, action, step_cost in get_successors(current):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
                    
        return []

    def dfs_search(self, start, goal, get_successors):
        frontier = []
        frontier.append((start, []))
        reached = set()

        while frontier:
            current, path = frontier.pop()

            if current == goal:
                return path

            if current not in reached:
                reached.add(current)
                for next_state, action, step_cost in get_successors(current):
                    if next_state not in reached:
                        frontier.append((next_state, path + [action]))

        return []

    def ucs_search(self, start, goal, get_successors):
        frontier = []
        import itertools
        counter = itertools.count()
        heapq.heappush(frontier, (0, next(counter), start, [])) 
        reached = {} 
        reached[start] = 0

        while frontier:
            cost, _, current, path = heapq.heappop(frontier)

            if current == goal:
                return path

            if current in reached and cost > reached[current]:
                continue

            for next_state, action, step_cost in get_successors(current):
                new_cost = cost + step_cost
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next(counter), next_state, path + [action]))

        return []