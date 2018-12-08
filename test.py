from gk import GraphState


def create_graph_state():
    g = GraphState(6)

    for i in g.nodes:
        g.h(i)

    g.cz(0, 1)
    g.cz(1, 2)
    g.cz(2, 0)
    g.cz(0, 3)
    g.cz(4, 5)

    return g


def test_random_outcomes():
    """ Testing random behaviour """
    ones = 0
    for i in range(1000):
        g = GraphState(1, vop="hadamard")
        g.h(0)
        ones += g._measure(0, "pz")
    assert 400 < ones < 600, "This is a probabilistic test!"


def test_single_qubit_measurements():
    """ Various simple tests of measurements """

    # Test that measuring |0> in Z gives 0
    g = GraphState(1, vop="hadamard")
    assert g._measure(0, "pz") == 0, "Measuring |0> in Z gives 0"

    # Test that measuring |1> in Z gives 1
    g = GraphState(1, vop="hadamard")
    g.x(0)
    assert g._measure(0, "pz") == 1, "Measuring |1> in Z gives 1"

    # Test that measuring |+> in X gives 0
    g = GraphState(1, vop="hadamard")
    g.h(0)
    assert g._measure(0, "px") == 0
    assert g._measure(0, "px") == 0, "Measuring |+> in X gives 0"
    g.z(0)
    assert g._measure(0, "px") == 1, "Measuring |-> in X gives 1"


def test_local_complementation():
    """ Test that local complementation works as expected """
    g = create_graph_state()
    g._local_complementation(0)
    assert g._edge(0, 1)
    assert g._edge(0, 2)
    assert not g._edge(1, 2)
    assert g._edge(3, 2)
    assert g._edge(3, 1)


def test_remove_vop():
    """ Test that removing VOPs really works """
    g = create_graph_state()
    g._remove_vop(0, 1)
    assert g.nodes[0]["vop"] == 0
    g._remove_vop(1, 1)
    assert g.nodes[1]["vop"] == 0
    g._remove_vop(2, 1)
    assert g.nodes[2]["vop"] == 0
    g._remove_vop(0, 1)
    assert g.nodes[0]["vop"] == 0


def test_cz():
    """ Test CZ gate """
    g = GraphState(2, vop="hadamard")
    g.h(0)
    g.h(1)
    g.y(1)
    assert not g._edge(0, 1)
    g.cz(0, 1)
    assert g._edge(0, 1)


test_local_complementation()
test_remove_vop()
test_cz()
test_single_qubit_measurements()
test_random_outcomes()
