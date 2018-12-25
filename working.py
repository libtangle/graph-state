from simulator import GraphState

n = 2

g = GraphState(n)
# g.h(0)
# g.h(1)

g.x(0)
g.h(1)
g.cz(0, 1)
g.h(1)

# print(g.statevector())
print(g.measure(0))