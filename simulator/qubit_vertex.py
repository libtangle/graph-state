from .vertex_operator import VertexOperator

class QubitVertex(object):
    def __init__(self):
        # Here, the VOP code is hardwritten in,
        # but you could get it with the method:
        # ```
        # self.vop = VertexOperator.from_name('H')
        # ````
        self.vop = VertexOperator(10)
        self.neighbors = set()
    
    def add_neighbor(self, a):
        """
        Add a neighbor to the vertex
        """
        self.neighbors.add(a)

    def remove_neighbor(self, a):
        """
        Remove a neighbor from the vertex
        """
        self.neighbors.discard(a)

    def has_neighbor(self, a):
        """
        Returns if this vertex has a given neighbor
        """
        return a in self.neighbors

    def neighbor_count(self):
        """
        Returns the number of neighbors this vertex has
        """
        return len(self.neighbors)
    
    def apply_vop(self, vop):
        self.vop = vop.multiply(self.vop)

    def __repr__(self):
        return "VOP: {}, Neighbors: {}".format(self.vop, self.neighbors)
