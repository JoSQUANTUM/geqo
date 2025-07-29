from geqo.core.quantum_operation import QuantumOperation


class BasicGate(QuantumOperation):
    """This class allows to define a unitary operation with a specified name and a specified number of qubits.
    For instance, a unitary gate with the name "CNOT" on two qubits is defined with ```BasicGate("CNOT", 2)```.
    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```InverseBasicGate```.

    Note that the definition of the corresponding unitary matrix depends on the chosen backend and must be
    defined with the function ```setValue``` of the backend.
    """

    def __init__(self, name, numberQubits):
        """
        The constructor of this class takes a name for the gate and the number of qubits.

        Parameters
        ----------
        name : String
            The name of this BasicGate.
        numberQubits : int
            The number of qubits, which this gate acts on.

        Returns
        -------
        InverseBasicGate : geqo.core.basic.BasicGate
            An object of this class that corresponds to the gate with the given name and qubits.
        """
        self.name = name
        self.numberQubits = numberQubits

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return 'BasicGate("' + self.name + '", ' + str(self.numberQubits) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same name and the same number of qubits.
        False : else
        """
        if not isinstance(other, BasicGate):
            return False
        return self.name == other.name and self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Return an object of the class ```InverseBasicGate```, which corresponds to the inverse of the gate. The name and the number of qubits are the same.

        Returns
        -------
        InverseBasicGate : geqo.core.basic.InverseBasicGate
            A new object of the class, which corresponds to the inverse gate.
        """
        return InverseBasicGate(self.name, self.numberQubits)

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this gate. Here, no ```Sequence``` object is returned because a basic gate cannot be decomposed.

        Returns
        -------

        None : None
            No ```Sequence``` object is returned because this gate cannot be decomposed.
        """
        return None

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this BasicGate.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this BasicGate.
        """
        return self.numberQubits

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
        False : Bool
            A BasicGate is considered to be as a non-decomposable operation.
        """
        return False

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True


class InverseBasicGate(QuantumOperation):
    """This class allows to define the inverse of a unitary operation with a specified name and a specified number of qubits.
    For instance, a unitary gate with the name "CNOT" on two qubits is defined with ```BasicGate("CNOT", 2)```.
    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```BasicGate```.

    Note that the definition of the corresponding unitary matrix depends on the chosen backend and must be
    defined with the function ```setValue``` of the backend.
    """

    def __init__(self, name, numberQubits):
        """
        The constructor of this class takes a name for the gate and the number of qubits.

        Parameters
        ----------
        name : String
            The name of this InverseBasicGate.
        numberQubits : int
            The number of qubits, which this gate acts on.

        Returns
        -------
        InverseBasicGate : geqo.core.basic.InverseBasicGate
            An object of this class that corresponds to the gate with the given name and qubits.
        """
        self.name = name
        self.numberQubits = numberQubits

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return 'InverseBasicGate("' + self.name + '", ' + str(self.numberQubits) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same name and the same number of qubits.
        False : else
        """
        if not isinstance(other, InverseBasicGate):
            return False
        return self.name == other.name and self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Return an object of the class ```BasicGate```, which corresponds to the inverse of the gate. The name and the number of qubits are the same.

        Returns
        -------
        BasicGate : geqo.core.basic.BasicGate
            A new object of the class, which corresponds to the inverse gate.
        """
        return BasicGate(self.name, self.numberQubits)

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this gate. Here, no ```Sequence``` object is returned because a basic gate cannot be decomposed.

        Returns
        -------

        None : None
            No ```Sequence``` object is returned because this gate cannot be decomposed.
        """
        return None

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this InverseBasicGate.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this InverseBasicGate.
        """
        return self.numberQubits

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
        False : Bool
            A BasicGate is considered to be as a non-decomposable operation.
        """
        return False

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True
