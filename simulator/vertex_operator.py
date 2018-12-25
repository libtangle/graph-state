from .lookup_tables import multiplication_table, vop_matrices, adjoint_table, measurement_conjugation_table

class VertexOperator(object):
    def __init__(self, code):
        self.code = code

    @staticmethod
    def from_name(name):
        codes = {
            'I': 0, # Identity Gate
            'X': 1, # Pauli X Gate
            'Y': 2, # Pauli Y Gate
            'Z': 3, # Pauli Z Gate
            'H': 10, # Hadamard Gate
            'spiZ': 5, # √(iZ) Gate
            'smiZ': 6, # √(-iZ) Gate
            'spiY': 11, # √(iY) Gate
            'smiY': 9, # √(-iY) Gate
            'spiX': 14, # √(iX) Gate
            'smiX': 15 # # √(-iX) Gate
        }

        return VertexOperator(codes[name])

    def multiply(self, vop):
        """Multiplies this operator with the specified local Clifford operator."""
        return VertexOperator(multiplication_table[self.code][vop.code])

    def pauli_conjugate(self, vop):
        """Get the conjugate of a Pauli"""
        # If this is the identity operator
        if self.code == 0:
            return 1
        
        if self.code > 3:
            raise ValueError("Conjugation can only be used with Paulis")
        
        if (vop.code & 0x03) == 0 or (vop.code & 0x03) == self.code:
            if vop.code >= 4 and vop.code < 14:
                zeta = 2
            else:
                zeta = 0
        else:
            if vop.code >= 4 and vop.code < 14:
                zeta = 0
            else:
                zeta = 2
        
        self.code = measurement_conjugation_table[self.code - 1][vop.code]
        return -1 if zeta == 2 else 1
  
    def adjoint(self):
        """Get the adjoint of the currrent vop"""
        return VertexOperator(adjoint_table[self.code])

    def get_matrix(self):
        """Get the matrix of the VOP"""
        return vop_matrices[self.code]


    def __repr__(self):
        return str(self.code)

