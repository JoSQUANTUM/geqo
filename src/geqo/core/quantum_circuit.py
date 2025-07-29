from geqo.core.quantum_operation import QuantumOperation


class Sequence(QuantumOperation):
    """This class allows to gather operations together in a single operation. It corresponds to
    a quantum circuit. A circuit consists of classical bits, qubits and a sequence of operations.

    The list of classical bits and qubits are specified by the
    arguments ```bits``` and ```qubits```, which can be numbers or character strings.

    The argument ```gatesAndTargets``` is a list of tuples and each element of the list
    is processed in the given order. A tuple consists of a quantum operation and one or two
    target specifications. If an operation only affects qubits, then the target specification
    is the list of corresponding qubits. If an operation affects classical bits as well as
    qubits, then the first target specification is a list of corresponding classical bits
    and the second target specification is a list of corresponding qubits.

    For convenience, the parameter ```name``` can be used to assign a name to the sequence.
    """

    def __init__(self, bits, qubits, gatesAndTargets, name=None):
        """
        The constructor of this class takes a list of bits and qubits. The operations and targets are
        also provided as a list of tuples or triples.

        Parameters
        ----------
        bits : list(int | String)
            The list of classical bits. Can be empty. A bit might be described by integers or by character strings.
        qubits : list(int | String)
            The list of quantum bits. Can be empty. A bit might be described by integers or by character strings.
        gatesAndTargets : list( (QuantumOperation, list(int | String)) | (QuantumOperation, list(int | String), list(int | String )))
            A tuple consists of the operation in the first component
            and the classical or quantum target in the second component, depending on the operation. An operation
            with classical and quantum targets are a triple in the list with the operation as the first component, the
            classical targets as second component and the quantum targets as third component.
        Sequence : geqo.core.quantum_circuit.Sequence
            A ```Sequence```, which contains the provided classical bits and qubits along with the operations and their targets.

        Returns
        -------
        PermuteQubits : geqo.algorithms.PermuteQubits
            An object of this class that corresponds to the specified permutation of qubits.
        """
        if len(qubits) > 1:
            for i in range(len(qubits)):
                if not isinstance(qubits[i], type(qubits[0])):
                    raise Exception("all qubit identifier must have the same type")

        if len(bits) > 1:
            for i in range(len(bits)):
                if not isinstance(bits[i], type(bits[0])):
                    raise Exception("all bit identifier must have the same type")

        self.bits = bits
        self.qubits = qubits
        self.gatesAndTargets = gatesAndTargets
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        if self.name is None:
            return (
                "Sequence("
                + str(self.bits)
                + ", "
                + str(self.qubits)
                + ", "
                + str(self.gatesAndTargets)
                + ")"
            )
        else:
            return (
                "Sequence("
                + str(self.bits)
                + ", "
                + str(self.qubits)
                + ", "
                + str(self.gatesAndTargets)
                + ', "'
                + str(self.name)
                + '")'
            )

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the classical bits and the qubits and the names and the list of operations and targets are the same.
        False : else
        """
        if not isinstance(other, Sequence):
            return False
        return (
            self.bits == other.bits
            and self.qubits == other.qubits
            and self.gatesAndTargets == other.gatesAndTargets
            and self.name == other.name
        )

    def getInverse(self):
        """
        Return an object of the same class, but each element of the list of operations is replaced by its inverse and the order of operations is reversed.
        Might raise an exception if an operation is not invertible.

        Returns
        -------
        Sequence : geqo.core.quantum_circuit.Sequence
            A new object of this class, which corresponds to the inverse operations.
        """
        newGatesAndTargets = []
        for i in range(len(self.gatesAndTargets))[::-1]:
            g = self.gatesAndTargets[i][0].getInverse()
            t = self.gatesAndTargets[i][1]
            newGatesAndTargets.append((g, t))
        return Sequence(self.bits, self.qubits, newGatesAndTargets)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence``` which corresponds to this object.

        Returns
        -------

        sequence : geqo.core.Sequence
            Returns the same object because it is an instantiation of the class ```Sequence```.
        """
        return self

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            A sequence is its own representation as object of the class ```Sequence```.
        """
        return True

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this operation.
        """
        return len(self.qubits)

    def getNumberClassicalBits(self):
        """
        Return the number of classical bits that are used by this operation.

        Returns
        -------
        numberBits : int
            The number of classical bits, which are used by this operation.
        """
        return len(self.bits)

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            If all gates in this ```Sequence``` are unitary.
        False : Bool
            Else.
        """
        for gate_and_target in self.gatesAndTargets:
            current_gate = gate_and_target[0]
            if not current_gate.isUnitary():
                return False
        return True
