from graph_state import GraphState
from collections import Counter

results = []
for i in range(1000):
  g = GraphState(2)
  g.apply(10, 0)
  g.apply(10, 1)
  g.cz(0, 1)
  g.apply(10, 1)

  if i == 0:
    g.draw()

  results.append(str(g.measure(0)) + str(g.measure(1)))

print(Counter(results))