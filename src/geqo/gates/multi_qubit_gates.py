from geqo.core.quantum_operation import QuantumOperation
from geqo.core.quantum_circuit import Sequence
from geqo.gates.fundamental_gates import CNOT, Hadamard, Phase


class Toffoli(QuantumOperation):
    """Toffoli (CCNOT) gate on three qubits."""

    def __init__(self, nameSpacePrefix=""):
        """
        The constructor of this class takes a name space prefix, which is used for the internal decomposition of this gate.

        Parameters
        ----------
        nameSpacePrefix : String
            This string is prepended to all names of internally used gates.

        Returns
        -------
        Toffoli : geqo.gates.multi_qubit_gates.Toffoli
            An object of this class that corresponds to the Toffoli gate, i.e. a double-controlled CNOT gate.
        """
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'Toffoli("{self.nameSpacePrefix}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the name space prefixes are the same.
        False : else
        """
        if not isinstance(other, Toffoli):
            return False
        else:
            return self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return the same object, because it is inverse to itself.

        Returns
        -------
        Toffoli : geqo.gates.multi_qubit_gates.Toffoli
            Return the object, because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains several operations that correspond to
        the Toffoli gate. The name space prefix is prepended to all internal gates when needed.

        Returns
        -------
        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
            The name space prefix is prepended to all internal gates when needed.
        """
        phPlusPi = Phase(self.nameSpacePrefix + "S.Pi/4")
        phMinusPi = Phase(self.nameSpacePrefix + "-S.Pi/4")
        seq = [
            (Hadamard(), [2]),
            (CNOT(), [1, 2]),
            (phMinusPi, [2]),
            (CNOT(), [0, 2]),
            (phPlusPi, [2]),
            (CNOT(), [1, 2]),
            (phMinusPi, [2]),
            (CNOT(), [0, 2]),
            (phPlusPi, [1]),
            (phPlusPi, [2]),
            (CNOT(), [0, 1]),
            (Hadamard(), [2]),
            (phPlusPi, [0]),
            (phMinusPi, [1]),
            (CNOT(), [0, 1]),
        ]
        return Sequence([], [0, 1, 2], seq)

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        3 : int
            The Toffoli gate acts on 3 qubits.
        """
        return 3

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by PermuteQubits, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The Toffoli gate can be decomposed into a sequence of simpler gates.
        """
        return True

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True
