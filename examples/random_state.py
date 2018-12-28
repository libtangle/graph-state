from graph_state import GraphState
import random

# Use 30 qubits
num_qubits = 30

g = GraphState(num_qubits)

# Apply 300000 operations
for i in range(300000):
  use_cz = random.choice([True, False])

  if use_cz:
    control, target = random.sample(range(num_qubits), 2)
    g.cz(control, target)
  else:
    operator = random.choice(range(24))
    target = random.choice(range(num_qubits))
    g.apply(operator, target)

g.draw()

# outcome = ''
# for i in range(num_qubits):
#   outcome += str(g.measure(i))

# print(outcome)