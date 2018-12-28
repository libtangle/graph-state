from graph_state import GraphState
from collections import Counter

results = []
for i in range(1000):
  g = GraphState(2)
  g.h(0)
  g.cx(0, 1)

  if i == 0:
    g.draw()

  results.append(str(g.measure(0)) + str(g.measure(1)))

print(Counter(results))