from precomputed import *
import random
import itertools as it


class GraphState(object):
    def __init__(self, num_qubits, **kwargs):
        self.adj = {}
        self.nodes = {}

        for n in range(num_qubits):
            self._add_node(n, **kwargs)

    def _add_node(self, id, vop="hadamard"):
        if id in self.nodes:
            print("Node {} already exists".format(id))
            return

        self.adj[id] = {}
        self.nodes[id] = {}
        self.nodes[id]['vop'] = vop_table[vop]

    def _apply_operation(self, target_id, operation):
        op = vop_table[operation]
        self.nodes[target_id]['vop'] = clifford_multiply(
            op, self.nodes[target_id]['vop'])

    def _edge(self, a, b):
        """Check if there is an edge between two verticles"""
        return b in self.adj[a]

    def _disconnected(self, a, b):
        return len(self.adj[a]) > (b in self.adj[a])

    def _remove_vop(self, a, b):
        # node, avoid
        others = set(self.adj[a]) - {b}
        c = others.pop() if others else b

        for s in reversed(decompositions[self.nodes[a]['vop']]):
            if s == 'x':
                self._local_complementation(a)
            else:
                self._local_complementation(c)

    def _local_complementation(self, a):
        n_v = self.adj[a]
        for i in n_v:
            for j in n_v:
                if i < j:
                    if self._edge(i, j):
                        self._remove_edge(i, j)
                    else:
                        self._add_edge(i, j)
            self.nodes[i]['vop'] = clifford_multiply(self.nodes[i]['vop'], 6)
        self.nodes[a]['vop'] = clifford_multiply(self.nodes[a]['vop'], 14)

    def _remove_edge(self, a, b):
        del self.adj[a][b]
        del self.adj[b][a]

    def _add_edge(self, a, b, data={}):
        self.adj[a][b] = data
        self.adj[b][a] = data

    def _apply_controlled_z(self, a, b):
        if self._disconnected(a, b):  # ngbh a\{b} !== {}
            self._remove_vop(a, b)
        if self._disconnected(b, a):  # ngbh b\{a} !== {}
            self._remove_vop(b, a)
        if self._disconnected(a, b):  # ngbh a\{b} !== {}
            # due to the removal above, the initial check must
            # be repeated.
            self._remove_vop(a, b)

        # Now it is sure that the condition ngbh c\{a, b} = {},
        # or VOP[c] in Z is fulfilled for c = a, b and we can use
        # lookup table

        edge = self._edge(a, b)
        vop_a = self.nodes[a]['vop']
        vop_b = self.nodes[b]['vop']
        new_edge, self.nodes[a]['vop'], self.nodes[b]['vop'] = cphase_table[
            int(edge), vop_a, vop_b]
        if new_edge != edge:
            if self._edge(a, b):
                self._remove_edge(a, b)
            else:
                self._add_edge(a, b)

    def _update_vop(self, v, op):
        """Update a VOP"""
        operation = vop_table[str(op)]
        self.nodes[v]['vop'] = clifford_multiplication_table[
            self.nodes[v]['vop'], operation]

    def _measure_graph_y(self, node, result):
        """Measure the bare graph in the Y-basis"""
        for a in self.adj[node]:
            self._update_vop(a, 'sqz' if result else 'msqz')

        ngbg = set(self.adj[node]) | {node}
        for i, j in it.combinations(ngbh, 2):
            if self._edge(i, j):
                self._remove_edge(i, j)
            else:
                self._add_edge(i, j)

        self._update_vop(node, 5 if result else 6)
        return result, False

    def _measure_graph_z(self, node, result):
        """Measure the bare graph in the Z-basis"""
        # Disconnect
        for neighbour in tuple(self.adj[node]):
            self._del_edge(node, neighbour)
            if result:
                self._update_vop(neighbour, "pz")

        # Rotate
        if result:
            self._update_vop(node, "px")
            self._update_vop(node, "hadamard")
        else:
            self._update_vop(node, "hadamard")

        return result, False

    def _measure_graph_x(self, node, result, friend=None):
        """ Measure the bare graph in the X-basis """
        if len(self.adj[node]) == 0:
            return 0, True

        # Pick a friend vertex
        if friend == None:
            friend = next(iter(self.adj[node].keys()))
        else:
            assert friend in list(
                self.adj[node].keys())  # TODO: unnecessary assert

        # Update the VOPs. TODO: pretty ugly
        if result:
            # Do a z on all ngb(vb) \ ngb(v) \ {v}, and some other stuff
            self._update_vop(friend, "msqy")
            self._update_vop(node, "pz")

            for n in set(self.adj[friend]) - set(self.adj[node]) - {node}:
                self._update_vop(n, "pz")
        else:
            # Do a z on all ngb(v) \ ngb(vb) \ {vb}, and sqy on the friend
            self._update_vop(friend, "sqy")
            for n in set(self.adj[node]) - set(self.adj[friend]) - {friend}:
                self._update_vop(n, "pz")

        # Toggle the edges. TODO: Yuk. Just awful!
        a = set(self.adj[node].keys())
        b = set(self.adj[friend].keys())
        if self._edge(a, b):
            self._remove_edge(a, b)
        else:
            self._add_edge(a, b)
        intersection = a & b
        for i, j in it.combinations(intersection, 2):
            if self._edge(i, j):
                self._remove_edge(i, j)
            else:
                self._add_edge(i, j)

        for n in a - {friend}:
            if self._edge(friend, n):
                self._remove_edge(friend, n)
            else:
                self._add_edge(friend, n)

        return result, False

    def _measure(self, target, basis):
        basis = vop_table[basis]
        ha = conjugation_table[self.nodes[target]['vop']]
        basis, phase = conjugate(basis, ha)

        # Make a random choice
        result = random.choice([0, 1])

        if basis == vop_table['px']:
            result, determinate = self._measure_graph_x(target, result)
        elif basis == vop_table['py']:
            result, determinate = self._measure_graph_y(target, result)
        elif basis == vop_table['pz']:
            result, determintate = self._measure_graph_z(target, result)
        else:
            raise ValueError("You can only measure in {X,Y,Z}")

        # Flip the result if there is a negative phase
        if phase == -1:
            result = not result

        return int(result)

    # Shorthand Gate Methods
    def h(self, target):
        self._apply_operation(target, 'hadamard')

    def s(self, target):
        self._apply_operation(target, 'phase')

    def phase(self, target):
        self._apply_operation(target, 'phase')

    def cz(self, control, target):
        self._apply_controlled_z(control, target)

    def y(self, target):
        self._apply_operation(target, 'py')

    def x(self, target):
        self._apply_operation(target, 'px')

    def z(self, target):
        self._apply_operation(target, 'pz')

    def measure_y(self, node):
        return self._measure(node, "py")

    def measure_z(self, node):
        return self._measure(node, "pz")

    def measure_x(self, node):
        return self._measure(node, 'px')
