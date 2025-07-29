from geqo.__logger__ import get_logger
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation

logger = get_logger(__name__)


class Measure(QuantumOperation):
    """This class allows to define a measurement operation. The argument ```numberQubits``` specifies
    the number of measured qubits. Besides the specified number of qubits, this operation also
    acts on the same number of classical bits for storing the measurement result.
    """

    def __init__(self, numberQubits):
        """
        The constructor of this class takes a number of qubits. Note that it also needs the same number of classical bits for storing the results of a measurement.

        Parameters
        ----------
        numberQubits : int
            The number of qubits, which this gate acts on. This is identical to the number of classical bits.

        Returns
        -------
        Measure : geqo.operations.measurement.Measure
            An object of this class that corresponds to the gate with the provided number of qubits.
        """
        self.numberQubits = numberQubits

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "Measure(" + str(self.numberQubits) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same number of qubits.
        False : else
        """
        if not isinstance(other, Measure):
            return False
        else:
            return self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Calling this method raises an exception because this operation has no inverse.
        """
        raise Exception("Measure has no inverse")

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this operation. A ```Sequence``` object is returned with this operation as only component in the list of operations.

        Returns
        -------

        Sequence : geqo.core.quantum_circuits.Sequence
            An object of the class```Sequence``` is returned with this operation and the appropriate quantum and classical targets in it.
        """
        numberQubits = self.getNumberQubits()
        allQubits = list(range(numberQubits))
        numberBits = self.getNumberQubits()
        allBits = list(range(numberBits))
        return Sequence(allBits, allQubits, [(self, allQubits, allBits)])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

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
        numberBits : int
            The number of classical bits, which are used by this operation.
        """
        return self.numberQubits

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
        False : Bool
            This is not a unitary operation.
        """
        return False


class DropQubits(QuantumOperation):
    """This operation allows to specify that a number of qubits are dropped from the
    system. This means, that the number of qubits of the system is reduced and the
    resulting state of the smaller system is calculated by tracing out the dropped
    qubits.

    For instance, ```DropQubits(1)``` corresponds to tracing out one qubit.
    """

    def __init__(self, numberQubits):
        """
        The constructor of this class takes a number of qubits.

        Parameters
        ----------
        numberQubits : int
            The number of qubits, which this gate acts on.

        Returns
        -------
        DropQubits : geqo.operations.measurement.DropQubits
            An object of this class that corresponds to the gate with the provided number of qubits.
        """
        self.numberQubits = numberQubits

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "DropQubits(" + str(self.numberQubits) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same number of qubits.
        False : else
        """
        if not isinstance(other, DropQubits):
            return False
        else:
            return self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Calling this method raises an exception because this operation has no inverse.
        """
        raise Exception("DropQubits has no inverse")

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this operation. A ```Sequence``` object is returned with this operation as only component in the list of operations.

        Returns
        -------

        Sequence : geqo.core.quantum_circuits.Sequence
            An object of the class```Sequence``` is returned with this operation and the appropriate quantum targets in it.
        """
        numberQubits = self.getNumberQubits()
        allQubits = list(range(numberQubits))
        numberBits = self.getNumberClassicalBits()
        allBits = list(range(numberBits))
        return Sequence(allBits, allQubits, [(self, allQubits)])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

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
            This operation is considered to be as a non-decomposable operation.
        """
        return False

    def isUnitary(self):
        """
        Returns
        -------
        False : Bool
            This is not a unitary operation.
        """
        return False
