from agent import SearchAgent

agent = SearchAgent()

start = (0, 0)
goal = (3, 4)

print(f"Testing Start: {start} | Goal: {goal}")
print("-" * 40)
print(f"Manhattan Distance: {agent.manhattan_distance(start, goal)}")
print(f"Euclidean Distance: {agent.euclidean_distance(start, goal)}")
