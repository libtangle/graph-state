# Gottesman-Knill Theorem

> A quantum circuit using only the following elements can be simulated efficiently on a classical computer:
> 1. Preperation of qubits in computational basis states.
> 2. Quantum gates from the Clifford group (Hadamard, CNOT and the Phase gate).
> 3. Measurement in the computational basis.

## Applications

* Entanglement Purification ([this paper](https://arxiv.org/abs/quant-ph/0512218))
* Quantum Error Correction

## Implementation

> See 'Fast simulation of stabilizer circuits using a graph state representation' by Simon Anders and Hans J. Briegel ([here](https://arxiv.org/abs/quant-ph/0504117v2))

### History

* The standard proof (as in the old Quantum Computing and Quantum Information) carries out the simulation in the time $\mathcal{O}(n^3)$, where $n$ is the number of qubits. Cubic scaling renders the simulation intractable for large numbers of qubits (as when entanglement purification is applied and when concatenating error correcting codes).
* Aaronson and Gottesman present a new algorithm (and implementation, CHP) in 'Improved simulation of stabilizer circuits' (2004). This brought an algorithm that scales in space and time only quadratically. This can be used for systems of thousands of qubits.
* Still, an even better algorithm was shown in the paper refered above, with time and space complexity of $\mathcal{O}(n \log n)$. This can be used for over a million qubits.

### Graph State

* This implementation is based around graph states.
These were introduced in the paper about entanglement purification ([here](https://arxiv.org/abs/quant-ph/0512218)) to study the entanglement properties of certain multi-qubit systems
* Takes their name from graphs in maths
* Each qubit corresponds to a vertex of the graph, and each edge indicates which qubits have interacted.
* There is a bijection between stabilizer states (the states that can appear in a stabilizer circuit) and graph states. That is, every graph state has a corresponding stabilizer state, and every stabilizer state has a corresponding graph state.
* This can be shown as: Any stabilizer state can be transformed to a graph state by applying a tensor product of local Clifford operations. These are known as *vertex operators* (VOPs). See [this paper](https://arxiv.org/abs/quant-ph/0111080) and [this paper](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.69.022316).
* The standard approach is to store a tableau of stabillzer operators (an $n \times n$ matrix of Pauli operators).
* The improved algorithm needs only the graph state and the list of VOPs, and requires space $\mathcal{O}(n \log n)$.
* To then change the state, measurement is studied in [this paper](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.69.062311), and gate application in [the paper mentioned above](https://arxiv.org/pdf/quant-ph/0504117v2.pdf).

## Definitions

### Clifford Group

> The Clifford group $\mathcal{C}_n$ on $n$ qubits is the normalizer of the Pauli group $\mathcal{P}_n$:
> $$
> \mathcal { C } _ { n } = \left\{ U \in S U \left( 2 ^ { n } \right) | U P U ^ { \dagger } \in \mathcal { P } _ { n } \quad \forall P \in \mathcal { P } _ { n } \right\},\\
> \mathcal{P}_n = \{\pm1, \pm i\} \cdot \{I, X, Y, Z\}^{\otimes n}.
> $$
>

