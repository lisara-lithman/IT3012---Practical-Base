# IT3012 - Intelligent Agents
## Practical 02 - Documentation

### Part 2: Theoretical Evaluation & Lecture Mapping

**1. (Remember) According to Lecture 02, why is it impossible to program a mathematically perfect "Table-Driven Agent" for complex environments like Chess? What happens as the agent's lifetime increases?**

According to the concept of combinatorial explosion, a mathematically perfect "Table-Driven Agent" relies on mapping every single possible percept sequence to an action. In complex environments like Chess, the number of possible states and the branching factor are astronomically large. As the agent's lifetime (the number of steps it takes) increases, the percept sequence history grows exponentially. Consequently, the lookup table size required to store all possible sequences becomes impossibly huge to compute, store, and access efficiently (for instance, a table for Chess would exceed the number of atoms in the observable universe).

**2. (Understand) Look at the code you wrote for your SimpleReflexAgent. Identify and explain the specific lines of code that represent the "Condition-Action Rules" discussed in the lecture.**

```python
if percept.get('food_here'): return 'Stay'
if percept.get('wall_ahead'): return 'Right'
return 'Up'
```
These specific lines directly map to the "Condition-Action Rules" (IF-THEN logic) of the Simple Reflex Agent architecture. The agent evaluates the current, immediate percept (the *Condition*)—such as `food_here` or `wall_ahead`—and instantly returns a hardcoded response (the *Action*) like `'Stay'`, `'Right'`, or `'Up'`. There is no reliance on memory or history, and the rules are triggered exclusively by what the sensors see in the present moment.

**3. (Analyze) Your SimpleReflexAgent likely got stuck in an infinite loop during Step 1.2. Based on the lecture, analyze exactly why this happened. How did the combination of "Partial Observability" and a lack of "Percept History" cause this failure?**

The Simple Reflex Agent operates in a Partially Observable environment, meaning its sensors only provide a limited view of the world (e.g., whether there is a wall immediately in front of it) rather than its exact global coordinates. Because the agent lacks a "Percept History" (internal state or memory), it cannot remember the cells it has already visited or the actions it just took. When it encounters a corner or a U-shaped obstacle, the limited percept looks exactly the same at each step in the cycle. The agent repeatedly executes the same sequence of rules (e.g., hit a wall -> turn right -> move up -> hit the wall again), completely unaware that it is repeating itself and thus gets permanently trapped in an infinite loop.

**4. (Evaluate) In Step 1.3, you added an internal state to your ModelBasedAgent. Evaluate how your specific code handles the "Transition Model" (how the world evolves) and the "Sensor Model" (how the agent's actions affect the world).**

In `ModelBasedAgent`, the **Transition Model** is handled by tracking the agent's simulated coordinate changes over time (`self.x`, `self.y`) and maintaining a history of explored space (`self.visited = {(0, 0)}` and `self.known_walls`). As the agent receives the current percept, it updates this internal map, reflecting how the environment looks based on what it has encountered so far. 

The **Sensor Model** (how actions affect the state) is represented through the `_get_offset` method and the `neighbor_map` logic. The agent evaluates how taking a specific action (e.g., 'Up') will alter its internal coordinates. Before taking an action, it checks how the action will transition its state (`dx, dy = self._get_offset(self.last_action)`) and cross-references it with its memory (`self.visited` and `self.known_walls`). By understanding the consequences of its movements in relation to its stored history, the agent can actively choose unvisited paths and successfully navigate out of loops.
