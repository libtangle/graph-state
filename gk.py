from precomputed import *


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
        new_edge, self.nodes[a]['vop'], self.nodes[b]['vop'] = cphase_table[int(
            edge), vop_a, vop_b]
        if new_edge != edge:
            if self._edge(a, b):
                self._remove_edge(a, b)
            else:
                self._add_edge(a, b)

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

    def __repr__(self):
        s = ""
        for key in sorted(self.nodes.keys()):
            s += "{}: {}\t".format(key,
                                   get_clifford_name(self.nodes[key]['vop']))
            if self.adj[key]:
                s += str(tuple(self.adj[key].keys())).replace(" ", "")
            else:
                s += "-"

            s += "\n"

        return s
