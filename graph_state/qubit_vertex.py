import networkx as nx

from .lookup_tables import multiplication_table

class QubitVertex(object):
  def __init__(self):
    self.vop_code = 10
    self.neighbors = set()

  def apply(self, vop):
    self.vop_code = multiplication_table[vop, self.vop_code]

  def apply_opposite(self, vop):
    self.vop_code = multiplication_table[self.vop_code, vop]

  def is_isolated(self, b):
    # ngbh a \ {b} = {}
    return len(self.neighbors - {b}) == 0

  def set_vop(self, vop):
    self.vop_code = vop

  def non_isolated(self, b):
    return self.neighbors - {b}

  def __str__(self):
    return "{} --> {}".format(self.vop_code, self.neighbors)