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


g = create_graph_state()
print(g.nodes)


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
