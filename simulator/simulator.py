import random

from .vertex_operator import VertexOperator
from .qubit_vertex import QubitVertex
from .lookup_tables import decomposition_table, cz_table

class GraphState(object):
    def __init__(self, num_qubits):
        """
        Create a new graph state with a given number of qubits.
        
        Each qubit is represented by a vertex.
        Each vertex is associated with a 'vertex operator', 
        associated with the qubit.
        """

        self.vertices = []
        for _ in range(num_qubits):
            self.vertices.append(QubitVertex())

    def add_edge(self, a, b):
        """Add an edge to the graph"""
        self.vertices[a].add_neighbor(b)
        self.vertices[b].add_neighbor(a)

    def remove_edge(self, a, b):
        """Remove an edge from the graph"""
        self.vertices[a].remove_neighbor(b)
        self.vertices[b].remove_neighbor(a)

    def toggle_edge(self, a, b):
        """Toggle an edge on the graph"""
        if self.vertices[a].has_neighbor(b):
            self.remove_edge(a, b)
        else:
            self.add_edge(a, b)

    def get_connection_info(self, a, b):
        """Find if the qubits are connected to eachother, 
        and to non-operand vertices"""
        was_edge = self.vertices[a].has_neighbor(b)
        if was_edge:
            non1 = self.vertices[a].neighbor_count() > 1
            non2 = self.vertices[b].neighbor_count() > 1
        else:
            non1 = self.vertices[a].neighbor_count() > 0
            non2 = self.vertices[b].neighbor_count() > 0
        return { 'non_1': non1, 'non_2': non2 }

    def local_complementation(self, a):
        ngbh = self.vertices[a].neighbors
        for v in ngbh:
            for u in ngbh:
                if v < u:
                    self.toggle_edge(v, u)
            self.vertices[v].apply_vop(VertexOperator(6)) # √(-iZ)
        self.vertices[a].apply_vop(VertexOperator(14)) # √(iX)
        
            
    def reduce_vop(self, a, b):
        """Reduce the VOP of a non isolated vertex, so that
        VOP[a] = I. This is done with a swapping partner, which
        (if possible) is not b"""

        # Iterate through, stop if we get to one that's not b.
        # If the loop doesn't break, then partner is b.
        for partner in self.vertices[a].neighbors:
            if partner != b:
                break

        d = decomposition_table[self.vertices[a].vop.code]
        for op in d:
            if op == 'U':
                self.local_complementation(a)
            else: # op == 'V'
                self.local_complementation(b)
    
    def apply(self, vop, target):
        """Apply a specific local operator on the
        target vertex"""
        self.vertices[target].apply_vop(vop)

    def cz(self, control, target):
        """Apply a controlled Z gate to the target vertex."""
        connection_info = self.get_connection_info(control, target)
        
        if connection_info['non_1']:
            self.reduce_vop(control, target)
            connection_info = self.get_connection_info(control, target)
        if connection_info['non_2']:
            self.reduce_vop(target, control)
            connection_info = self.get_connection_info(control, target)
        if connection_info['non_1']:
            self.reduce_vop(control, target)
            connection_info = self.get_connection_info(control, target)
        
        control_vop = self.vertices[control].vop.code
        target_vop = self.vertices[target].vop.code
        
        # toggle edge

        edge = 1 if self.vertices[control].has_neighbor(target) else 0
        lookup = cz_table[edge][control_vop][target_vop]

        if lookup[0] != 0:
            self.add_edge(control, target)
        else:
            self.remove_edge(control, target)

        self.vertices[control].vop.code = lookup[1]
        self.vertices[target].vop.code = lookup[2]
    
    def measure(self, target):
        """Measure in the Z basis"""
        # BEGIN BARE MEASURE
        choice = random.choice([0, 1])

        for v in self.vertices[target].neighbors:
            self.remove_edge(target, v)
            if choice == 1:
                self.z(v)
        
        if choice == 1:
            self.x(target)
        self.h(target)
        # END BARE MEASURE

        # Get the phase
        rp = VertexOperator(3).pauli_conjugate(self.vertices[target].vop.adjoint())
        
        if rp == -1:
            choice ^= 1
        elif rp != 1:
            raise ValueError("Illegal phase unequal to 1: {}", rp)

        return choice

    def statevector(self):
        """Compute the statevector"""
        import numpy as np
        from itertools import combinations
        import qcgpu


        state = qcgpu.State(len(self.vertices))
        # state = np.eye(2 ** len(self.vertices))

        for i, val in enumerate(self.vertices):
            state.h(i)

        possible_edges = list(combinations(range(len(self.vertices)), 2))
        edges = [(a, b) for [a, b] in possible_edges if self.vertices[a].has_neighbor(b)]
        for i,j in edges:
            state.apply_controlled_gate(qcgpu.gate.z(), i, j)
        
        for i, vert in enumerate(self.vertices):
            gate = qcgpu.Gate(vert.vop.get_matrix())
            state.apply_gate(gate, i)
        return state.amplitudes()
        # c = reduce(np.kron, matrices, 1)
        

    def h(self, target):
        """Apply a Hadamard gate to the target"""
        self.apply(VertexOperator(10), target)

    def x(self, target):
        """Apply a Pauli X gate to the target"""
        self.apply(VertexOperator(1), target)

    def y(self, target):
        """Apply a Pauli Y gate to the target"""
        self.apply(VertexOperator(2), target)

    def z(self, target):
        """Apply a Pauli Z gate to the target"""
        self.apply(VertexOperator(3), target)

    def s(self, target):
        """Apply an S/phase gate to the target"""
        self.apply(VertexOperator(6), target)

    def __repr__(self):
        return str(self.vertices)