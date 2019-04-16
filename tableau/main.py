import numpy as np

class state:
    def __init__(self, num_qubits):
        self.n = num_qubits
        self.tableau = np.eye(2 * num_qubits, dtype=np.int8)
        self.phase = np.zeros((2 * num_qubits, 1), dtype=np.int8)

    def h(self, a):
        for i in range(2 * self.n):
            self.phase[i] ^= (self.tableau[i, a] * self.tableau[i , self.n * a])

            # Swap x_ia with z_ia
            # There is probably a better way to do this
            temp = self.tableau[i, a]
            self.tableau[i, a] = self.tableau[i, self.n + a]
            self.tableau[i, self.n + a] = temp

    def s(self, a):
        for i in range(2 * self.n):
            self.phase[i] ^= (self.tableau[i, a] * self.tableau[i , self.n * a])
            self.tableau[i, self.n + a] ^= self.tableau[i, a]

    # a = control, b = target
    def cx(self, a, b):
        for i in range(2 * self.n):
            self.phase[i] ^= self.tableau[i, a] * self.tableau[i, self.n + a] * (self.tableau[i, b] ^ self.tableau[i, self.n + a] ^ 1)
            self.tableau[i, b] ^= self.tableau[i, a]
            self.tableau[i, self.n + a] ^= self.tableau[i, self.n + b]

    def measure(self, a):
        found = False

        for p in range(self.n, 2 * self.n):
            if self.tableau[p, a] = 1:
                if found:
                    found = min(p, found)
                else:
                    found = p

        

    def __str__(self):
        return np.array2string(self.tableau)

s = state(3)
s.h(0)
s.cx(0, 1)

print(s)
print(s.phase)
