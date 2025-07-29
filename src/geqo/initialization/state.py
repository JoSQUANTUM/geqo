from geqo.__logger__ import get_logger
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation

logger = get_logger(__name__)


class SetBits(QuantumOperation):
    """This operations allows to set the values of classical bits.

    For instance, the operation ```setBits("values", 3)``` sets
    three classical bits to the values with the name ```values```.

    Note that the definition of ```values``` depends on the chosen
    backend and must be defined with the function ```setValue``` of the backend.
    """

    def __init__(self, name, numberBits):
        """
        The constructor of this class takes a name for the bit settings and the number of bits.

        Parameters
        ----------
        name : String
            The name of the bit vector to be used for setting the bits.
        numberBits : int
            The number of classical bits, on which the operator acts.

        Returns
        -------
        SetBits : geqo.initialization.state.SetBits
            An object that corresponds to setting classical bits to specific values.
        """
        self.name = name
        self.numberBits = numberBits

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return 'SetBits("' + self.name + '", ' + str(self.numberBits) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same name and the same number of bits.
        False : else
        """
        if not isinstance(other, SetBits):
            return False
        else:
            return self.name == other.name and self.numberBits == other.numberBits

    def getInverse(self):
        """
        Calling this method raises an exception because this operation has no inverse.
        """
        logger.error("SetBits has no inverse")
        raise Exception("SetBits has no inverse")

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this gate. A ```Sequence``` object is returned with this operation as only component in the list of operations.

        Returns
        -------

        Sequence : geqo.core.quantum_circuits.Sequence
            An object of the class```Sequence``` is returned with this operation and the appropriate classical targets in it.
        """
        allBits = list(range(self.numberBits))
        return Sequence(allBits, [], [(self, allBits)])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        0 : int
            This operation only acts on classical bits.
        """
        return 0

    def getNumberClassicalBits(self):
        """
        Return the number of classical bits that are used by this operation.

        Returns
        -------
        numberBits : int
            This operation acts on the specified number of classical bits.
        """
        return self.numberBits

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
        False : Bool
            This is not a unitary operation.
        """
        return False


class SetQubits(QuantumOperation):
    """This operations allows to set the values of qubits.

    For instance, the operation ```setQubits("values", 3)``` sets
    three qubits to either |0> or |1> with the name ```values```.

    Note that the definition of ```values``` depends on the chosen
    backend and must be defined with the function ```setValue``` of the backend.

    """

    def __init__(self, name, numberQubits):
        """
        The constructor of this class takes a name for the qubit settings and the number of qubits.

        Parameters
        ----------
        name : String
            The name of the bits to be used for setting the qubits in the standard basis.
        numberQubits : int
            The number of qubits, on which the operator acts.

        Returns
        -------
        SetQubits : geqo.initialization.state.SetQubits
            An object that corresponds to setting qubits to a specific state in the standard basis.
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
        return 'SetQubits("' + self.name + '", ' + str(self.numberQubits) + ")"

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
        if not isinstance(other, SetQubits):
            return False
        else:
            return self.name == other.name and self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Calling this method raises an exception because this operation has no inverse.
        """
        logger.error("SetQubits has no inverse")
        raise Exception("SetQubits has no inverse")

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this gate. A ```Sequence``` object is returned with this operation as only component in the list of operations.

        Returns
        -------

        Sequence : geqo.core.quantum_circuits.Sequence
            An object of the class```Sequence``` is returned with this operation and the appropriate quantum targets in it.
        """
        allQubits = list(range(self.numberQubits))
        return Sequence([], allQubits, [(self, allQubits)])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        numberQubits : int
            This operation only acts on the specified number of qubits.
        """
        return self.numberQubits

    def getNumberClassicalBits(self):
        """
        Return the number of classical bits that are used by this operation.

        Returns
        -------
        0 : int
            This operation only acts on quantum bits.
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
        False : Bool
            This is not a unitary operation.
        """
        return False


class SetDensityMatrix(QuantumOperation):
    """This class allows to set the density matrix of one or more qubits. Before the
    state is set, the affected qubits are traced out, leading to a mixed state in
    general.

    For instance, the operation ```SetDensityMatrix("ρ", 2)``` sets two qubits to
    the density matrix with the name ```ρ```.

    Note that the definition of the corresponding density matrix depends on the
    chosen backend and must be defined with the function ```setValue``` of the backend.
    """

    def __init__(self, name, numberQubits):
        """
        The constructor of this class takes a name for the bit settings and the number of qubits.

        Parameters
        ----------
        name : String
            The name of the density matrix to be used for setting the qubits.
        numberQubits : int
            The number of qubits, on which the operator acts.

        Returns
        -------
        SetDensityMatrix : geqo.initialization.state.SetDensityMatrix
            An object that corresponds to setting the state of qubits to a specific density matrix with the given name.
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
        return 'SetDensityMatrix("' + self.name + '", ' + str(self.numberQubits) + ")"

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
        if not isinstance(other, SetDensityMatrix):
            return False
        else:
            return self.name == other.name and self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Calling this method raises an exception because this operation has no inverse.
        """
        logger.error("SetDensityMatrix has no inverse")
        raise Exception("SetDensityMatrix has no inverse")

    def getEquivalentSequence(self):
        """
        Return a sequence, which is equivalent to this gate. A ```Sequence``` object is returned with this operation as only component in the list of operations.

        Returns
        -------

        Sequence : geqo.core.quantum_circuits.Sequence
            An object of the class```Sequence``` is returned with this operation and the appropriate quantum targets in it.
        """
        allQubits = list(range(self.numberQubits))
        return Sequence([], allQubits, [(self, allQubits)])

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation.

        Returns
        -------
        numberQubits : int
            This operation only acts on the specified number of qubits.
        """
        return self.numberQubits

    def getNumberClassicalBits(self):
        """
        Return the number of classical bits that are used by this operation.

        Returns
        -------
        0 : int
            This operation only acts on quantum bits.
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
        False : Bool
            This is not a unitary operation.
        """
        return False
