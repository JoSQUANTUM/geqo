from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation


class PauliX(QuantumOperation):
    """Pauli X gate on one qubit."""

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        PauliX : geqo.core.fundamental_gates.PauliX
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "PauliX()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, PauliX):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return the object itself because it is self-inverse.

        Returns
        -------
        PauliX : geqo.core.fundamental_gates.PauliX
            The same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class PauliY(QuantumOperation):
    """Pauli Y gate on one qubit."""

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        PauliY : geqo.core.fundamental_gates.PauliY
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "PauliY()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, PauliY):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return the object itself because it is self-inverse.

        Returns
        -------
        PauliY : geqo.core.fundamental_gates.PauliY
            The same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class PauliZ(QuantumOperation):
    """Pauli Z gate on one qubit."""

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        PauliZ : geqo.core.fundamental_gates.PauliZ
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "PauliZ()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, PauliZ):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return the object itself because it is self-inverse.

        Returns
        -------
        PauliZ : geqo.core.fundamental_gates.PauliZ
            The same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class Hadamard(QuantumOperation):
    """Hadamard gate on one qubit."""

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        Hadamard : geqo.core.fundamental_gates.Hadamard
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "Hadamard()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, Hadamard):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return the object itself because it is self-inverse.

        Returns
        -------
        Hadamard : geqo.core.fundamental_gates.Hadamard
            The same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class Phase(QuantumOperation):
    """Phase shift gate on one qubit."""

    def __init__(self, name):
        """
        The constructor of this class. The name of the angle is a parameter.

        Parameters
        ----------
        name : String
            The name of the phase.

        Returns
        -------
        Phase : geqo.core.fundamental_gates.Phase
            An object of this class. It has no parameters.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'Phase("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class and has the same name.
        False : else
        """
        if not isinstance(other, Phase):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```InversePhase```, which has the same name.

        Returns
        -------
        InversePhase : geqo.core.fundamental_gates.InversePhase
            Return an object of the class ```InversePhase``` with the same name. It corresponds to the inverse of this operation.
        """
        return InversePhase(self.name)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class InversePhase(QuantumOperation):
    """Inverse phase shift gate on one qubit."""

    def __init__(self, name):
        """
        The constructor of this class. The name of the angle is a parameter.

        Parameters
        ----------
        name : String
            The name of the phase.

        Returns
        -------
        InversePhase : geqo.core.fundamental_gates.InversePhase
            An object of this class. It has no parameters.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'InversePhase("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class and has the same name.
        False : else
        """
        if not isinstance(other, InversePhase):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```Phase```, which has the same name.

        Returns
        -------
        Phase : geqo.core.fundamental_gates.Phase
            Return an object of the class ```Phase``` with the same name. It corresponds to the inverse of this operation.
        """
        return Phase(self.name)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class CNOT(QuantumOperation):
    """CNOT gate on two qubits."""

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        CNOT : geqo.core.fundamental_gates.CNOT
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "CNOT()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, CNOT):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return the object itself because it is self-inverse.

        Returns
        -------
        CNOT : geqo.core.fundamental_gates.CNOT
            The same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0, 1], [(self, [0, 1])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by this gate.
        """
        return 2

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
            This operation is considered to be as a non-decomposable operation.
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


class SwapQubits(QuantumOperation):
    """Swap gate on two qubits."""

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        SwapQubits : geqo.core.fundamental_gates.SwapQubits
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "SwapQubits()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, SwapQubits):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return the object itself because it is self-inverse.

        Returns
        -------
        SwapQubits : geqo.core.fundamental_gates.SwapQubits
            The same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0, 1], [(self, [0, 1])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by this gate.
        """
        return 2

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
            This operation is considered to be as a non-decomposable operation.
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


class SGate(QuantumOperation):
    """This operation corresponds to the square root of the Z gate on one qubit.

    For the definition, see ```https://en.wikipedia.org/wiki/Clifford_gates#S_gate```.
    """

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        SGate : geqo.core.fundamental_gates.SGate
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "SGate()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, SGate):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return an object of the class ```InverseSGate```.

        Returns
        -------
        InverseSGate : geqo.gates.fundamental_gates.InverseSGate
            A new object of this class, which corresponds to the inverse operation.
        """
        return InverseSGate()

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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


class InverseSGate(QuantumOperation):
    """This operation corresponds to the inverse of the square root of the Z gate on one qubit.

    For the definition of the S gate, see ```https://en.wikipedia.org/wiki/Clifford_gates#S_gate```.
    """

    def __init__(self):
        """
        The constructor of this class. It has no parameters.

        Returns
        -------
        InverseSGate : geqo.core.fundamental_gates.InverseSGate
            An object of this class. It has no parameters.
        """
        pass

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "InverseSGate()"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same class.
        False : else
        """
        if not isinstance(other, InverseSGate):
            return False
        else:
            return True

    def getInverse(self):
        """
        Return an object of the class ```SGate```.

        Returns
        -------
        SGate : geqo.gates.fundamental_gates.SGate
            A new object of this class, which corresponds to the inverse operation.
        """
        return SGate()

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because this
        operation is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Sequence([], [0], [(self, [0])])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this gate.
        """
        return 1

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
            This operation is considered to be as a non-decomposable operation.
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
