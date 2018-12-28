import itertools as it
import random

from .qubit_vertex import QubitVertex
from .lookup_tables import measure_table, decomposition_table, conjugation_table, cz_table

class GraphState(object):
  def __init__(self, num_nodes):
    self.vertices = []

    for i in range(num_nodes):
      self.vertices.append(QubitVertex())
  
  ########################################################
  # Simulation Methods
  ########################################################

  def apply(self, vop, target):
    self.vertices[target].apply(vop)

  def h(self, target):
    self.apply(10, target)

  def x(self, target):
    self.apply(1, target)
  
  def y(self, target):
    self.apply(2, target)
  
  def z(self, target):
    self.apply(3, target)

  def id(self, target):
    pass

  def s(self, target):
    self.apply(6, target)

  def s_dagger(self, target):
    self.apply(5, target)

  def cz(self, control, target):
    if self.vertices[control].is_isolated(target):
      self.reduce_vop(control, target)

    if self.vertices[target].is_isolated(control):
      self.reduce_vop(target, control)

    if self.vertices[control].is_isolated(target): 
      self.reduce_vop(control, target)

    has_edge = self.has_edge(control, target)
    control_vop = self.vertices[control].vop_code
    target_vop = self.vertices[target].vop_code
    
    edge, control_vop, target_vop = cz_table[int(has_edge), control_vop, target_vop]
    self.vertices[control].set_vop(control_vop)
    self.vertices[target].set_vop(target_vop)
    if has_edge != edge:
      self.toggle_edge(control, target)

  def measure(self, target, basis='Z'):
    if basis == 'X':
      basis = 1
    elif basis == 'Y':
      basis = 2
    else:
      basis = 3

    vop_conjugate = conjugation_table[self.vertices[target].vop_code]
    bare_basis, phase = measure_table[basis, vop_conjugate]

    # Choose a result
    choice = random.choice([0, 1])

    if bare_basis == 1:
      choice = self.bare_measure_x(target, choice)
    elif bare_basis == 2:
      choice = self.bare_measure_y(target, choice)
    else:
      choice = self.bare_measure_z(target, choice)
    
    # Flip the result if there is a negative phase
    if phase == -1:
      choice = not choice
    
    return int(choice)

  def cx(self, control, target):
    self.h(target)
    self.cz(control, target)
    self.h(target)

  ########################################################
  # Computation Algorithms see https://arxiv.org/abs/quant-ph/0504117.pdf)
  ########################################################

  def reduce_vop(self, a, b):
    # First, we choose a swapping partner c
    external = self.vertices[a].non_isolated(b)
    c = external.pop() if external else b

    d = decomposition_table[self.vertices[a].vop_code]
    for factor in reversed(d):
      if factor == 'X':
        # Factor is sqrt(-iX)
        self.local_complementation(a)
      else:
        # Factor is sqrt(iZ)
        self.local_complementation(b)
    
    # Now the vertex operator of a is `0`, 
    # the identity operator.

  def local_complementation(self, a):
    ngbh = self.vertices[a].neighbors.copy()

    for i, j in it.combinations(ngbh, 2):
      self.toggle_edge(i, j)

    self.vertices[a].apply_opposite(14)
    for i in self.vertices[a].neighbors:
      self.vertices[i].apply_opposite(6)
  
  def bare_measure_x(self, target, choice):
    # If the vertex is isolated, measurement will
    # always be a zero.
    ngbh = self.vertices[target].neighbors.copy() 
    if len(self.vertices[target].neighbors) == 0:
      return 0

    b = next(iter(ngbh))

    if choice == 1:
      self.vertices[b].apply_opposite(9)
      self.vertices[target].apply_opposite(3)
      
      for n in self.vertices[b].neighbors - self.vertices[target].neighbors - {target}:
        self.vertices[n].apply_opposite(3)
    else:
      self.vertices[b].apply_opposite(11)

      for n in self.vertices[target].neighbors - self.vertices[b].neighbors - {b}:
        self.vertices[n].apply_opposite(3)

    ngbh_a = self.vertices[target].neighbors
    ngbh_b = self.vertices[b].neighbors
    self.toggle_edges(ngbh_a, ngbh_b)

    shared_edges = ngbh_a & ngbh_b
    for i, j in it.combinations(shared_edges, 2):
      self.toggle_edge(i, j)

    for n in ngbh_a - {b}:
      self.toggle_edge(b, n)
    
    return choice



  def bare_measure_y(self, target, choice):
    for n in self.vertices[target].neighbors:
      self.vertices[target].apply_opposite(5 if choice else 6)
    
    for i, j in it.combinations(self.vertices[target].neighbors | {target} , 2):
      self.toggle_edge(i, j)
    
    self.vertices[target].apply_opposite(5 if choice else 6)
    return choice

  def bare_measure_z(self, target, choice):
    for n in self.vertices[target].neighbors.copy():
      self.remove_edge(target, n)
      if choice:
        self.vertices[n].apply_opposite(3)

    if choice:
      self.vertices[target].apply_opposite(1)

    self.vertices[target].apply_opposite(10) 

    return choice
  
  ########################################################
  # Graph Methods
  ########################################################

  def toggle_edge(self, a, b):
    if self.has_edge(a, b):
      self.remove_edge(a, b)
    else:
      self.add_edge(a, b)

  def has_edge(self, a, b):
    return b in self.vertices[a].neighbors or a in self.vertices[b].neighbors
  
  def add_edge(self, a, b):
    self.vertices[a].neighbors.add(b)
    self.vertices[b].neighbors.add(a)

  def remove_edge(self, a, b):
    self.vertices[a].neighbors.remove(b)
    self.vertices[b].neighbors.remove(a)

  def edges(self):
    possible_edges = it.combinations(range(len(self.vertices)), 2)
    return [(a, b) for [a, b] in possible_edges if self.has_edge(a, b)]

  def toggle_edges(self, a, b):
    done = set()
    for i, j in it.product(a, b):
      if i != j and not (i, j) in done:
        done.add((i, j))
        done.add((j, i))
        self.toggle_edge(i, j)

  ########################################################
  # Helper Methods (for things such as drawing)
  ########################################################

  def __str__(self):
    res = ''

    for idx, v in enumerate(self.vertices):
      res += '[{}]: {}\n'.format(idx, v)

    return res

  def to_networkx(self):
    import networkx as nx
    G = nx.Graph()
    
    for idx, v in enumerate(self.vertices):
      G.add_node(idx)
      for u in v.neighbors:
        
        G.add_edge(idx, u)
      G.nodes[idx]['vop'] = v.vop_code
    
    return G

  def draw(self):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = self.to_networkx()

    pos_nodes = nx.spring_layout(G)
    nx.draw(G, pos_nodes, with_labels=True)

    pos_attrs = {}
    for node, coords in pos_nodes.items():
        pos_attrs[node] = (coords[0], coords[1] + 0.08)

    node_attrs = nx.get_node_attributes(G, 'vop')
    custom_node_attrs = {}
    for node, attr in node_attrs.items():
        custom_node_attrs[node] = attr

    nx.draw_networkx_labels(G, pos_attrs, labels=custom_node_attrs)
    plt.show()
