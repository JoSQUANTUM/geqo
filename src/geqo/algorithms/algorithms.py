from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.gates.fundamental_gates import Hadamard, Phase, SwapQubits, PauliX
from geqo.gates.rotation_gates import Rx, Ry
from geqo.gates.multi_qubit_gates import Toffoli
from geqo.operations.controls import QuantumControl


class PermuteQubits(QuantumOperation):
    """This class allows to define a unitary operation that corresponds to a permutation
    of qubits. The argument is the target order of the permuted qubits, which are denoted
    by 0, ..., n-1 for n qubits.

    For instance, ```PermuteQubits([2,1,0])``` defines the bit reversal on three qubits.
    """

    def __init__(self, targetOrder):
        """
        The constructor of this class takes a permutation in list representation as input. For
        instance, the targetOrder [2,1,0] corresponds to a reversed order of qubits.

        Parameters
        ----------
        targetOrder : list(int)
                      The new order of qubits after the permutation. The order is
                      represented as a list of indices, starting with 0 as index of
                      the first qubit.

        Returns
        -------
        PermuteQubits : geqo.algorithms.PermuteQubits
            An object of this class that corresponds to the specified permutation of qubits.
        """
        self.targetOrder = targetOrder

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = "PermuteQubits(" + str(self.targetOrder) + ")"
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it corresponds to the same permutation of qubits.
        False : else
        """
        if not isinstance(other, PermuteQubits):
            return False
        return self.targetOrder == other.targetOrder

    def getInverse(self):
        """
        Return an object of the same class, but it corresponds to the inverse permutation of qubits as this object.

        Returns
        -------
        PermuteQubits : geqo.algorithm.PermuteQubits
            A new object of this class, which corresponds to the inverse permutation of qubits.
        """

        newOrder = []
        for x in range(len(self.targetOrder)):
            newOrder.append(self.targetOrder.index(x))
        return PermuteQubits(newOrder)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which does not contain any operators, because a
        permutation of qubits is considered to be as a non-decomposable operation.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        numberQubits = self.getNumberQubits()
        allQubits = list(range(numberQubits))
        sequence = Sequence([], allQubits, [(self, allQubits)])
        return sequence

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this permutation of qubits. This is equal
            to the length of the list representation of the permuation.
        """
        numberQubits = len(self.targetOrder)
        return numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by PermuteQubits, is zero.
        """
        return 0

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True

    def hasDecomposition(self):
        """
        Returns
        -------
        False : Bool
            A permutation of qubits is considered to be as a non-decomposable operation.
        """
        return False


class QubitReversal(QuantumOperation):
    """This operation is reversing the order of qubits. It corresponds to a permutation of the
    states of the computational basis.

    See ```https://en.wikipedia.org/wiki/Bit-reversal_permutation``` for the related bit-reversal permutation.
    """

    def __init__(self, numberQubits):
        """
        The constructor of this class takes the number of qubits as input.

        Parameters
        ----------
        numberQubits : int
                      The number of qubits for this qubit reversal operation.

        Returns
        -------
        QubitReversal : geqo.algorithms.QubitReversal
            An object of this class that corresponds to the specified qubit reversal operation.
        """
        self.numberQubits = numberQubits

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = "QubitReversal(" + str(self.numberQubits) + ")"
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same number of qubits.
        False : else
        """
        if not isinstance(other, QubitReversal):
            return False
        return self.numberQubits == other.numberQubits

    def getInverse(self):
        """
        Return this object because the reversal of qubits is inverse to itself.

        Returns
        -------
        QubitReversal : geqo.algorithm.QubitReversal
            Return the same object because it is self-inverse.
        """
        return self

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of qubit swaps. The sequence of swaps
        correspond to the qubit reversal.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with swap operations and the appropriate bits and qubits.
        """
        numberQubits = self.getNumberQubits()
        allQubits = list(range(numberQubits))
        seq = []
        for i in range(numberQubits // 2):
            seq.append((SwapQubits(), [i, numberQubits - i - 1]))
        return Sequence([], allQubits, seq)

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this qubit reversal operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this qubit reversal.
        """
        numberQubits = self.numberQubits
        return numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by this qubit reversal operation, is zero.
        """
        return 0

    def isUnitary(self):
        """
        Returns
        -------
        True : Bool
            This is a unitary operation.
        """
        return True

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The qubit reversal can be decomposed into a sequence of qubit swaps.
        """
        return True


class QFT(QuantumOperation):
    """This operation corresponds to the quantum Fourier transform on a specified number of qubits.

    For the definition, see ```https://en.wikipedia.org/wiki/Quantum_Fourier_transform```.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```InverseQFT```.


    The QFT can be decomposed into a sequence of controlled phase operations and Hadamard gates, see
    ```https://en.wikipedia.org/wiki/Toffoli_gate#Related_logic_gates``` for details.

    This decomposition can be obtained with the function ```getEquivalentSequence```. It returns
    a sequence of Hadamard gates and gates of the class Phase with the names ```Ph1```, ```Ph2``, ...
    where ```Phk``` corresponds to a phase gate with phase $e^{2pi i/2^k}.

    For instance, the QFT on two qubits
    corresponds to the sequence ```Sequence([], [0, 1], [(Hadamard(), [0]), (QuantumControl([1], Phase("Ph1")), [1, 0]), (Hadamard(), [1]), (QubitReversal(2), [0, 1])])``` where ```Ph1```
    denotes

    To avoid conflicts with the names of other gates, a name space prefix can be provided to the
    contructor of QFT. For instance, the object ```QFT(2, "test.")``` leads to the sequence
    ```Sequence([], [0, 1], [(Hadamard(), [0]), (QuantumControl([1], Phase("test.Ph1")), [1, 0]), (Hadamard(), [1]), (QubitReversal(2), [0, 1])])```.

    For convenience, a backend might be prepared for applying a QFT with the function ```prepareBackend```
    of the corresponding backend class.
    """

    def __init__(self, numberQubits, nameSpacePrefix=""):
        """
        The constructor of this class takes a the number of qubits and an optional name space prefix as
        parameters.

        Parameters
        ----------
        numberQubits : int
                      The number of qubits, which the QFT acts on.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        QFT : geqo.algorithms.QFT
            An object of this class that corresponds to the QFT.
        """
        self.numberQubits = numberQubits
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            "QFT(" + str(self.numberQubits) + ', "' + self.nameSpacePrefix + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same number of qubits and the same name space prefix.
        False : else
        """
        if not isinstance(other, QFT):
            return False
        return (
            self.numberQubits == other.numberQubits
            and self.nameSpacePrefix == other.nameSpacePrefix
        )

    def getInverse(self):
        """
        Return an object of the class ```InverseQFT``` with the same number of qubits and the same name space prefix.

        Returns
        -------
        InverseQFT : geqo.algorithm.InverseQFT
            A new object of this class, which corresponds to the inverse QFT.
        """
        return InverseQFT(self.numberQubits, self.nameSpacePrefix)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of Hadamard and controlled phase gates. The sequence of gates
        correspond to the QFT.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with Hadamard and controlled phase operations and the appropriate bits and qubits.
        """
        h = Hadamard()
        n = self.numberQubits
        seq = []
        for i in range(n):
            seq.append((h, [i]))
            for j in range(1, n - i):
                seq.append(
                    (
                        QuantumControl(
                            [1], Phase(self.nameSpacePrefix + "Ph" + str(j))
                        ),
                        [i + j, i],
                    )
                )
        seq.append((QubitReversal(n), list(range(n))))
        return Sequence([], list(range(n)), seq)

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this QFT operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this QFT operation.
        """
        numberQubits = self.numberQubits
        return numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by the QFT, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The QFT can be decomposed into a sequence of Hadamard gates and controlled phase gates and a qubit reversal.
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


class InverseQFT(QuantumOperation):
    """This operation corresponds to the inverse of the quantum Fourier transform on a specified
    number of qubits.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```QFT```.

    For more information, please refer to the documentation of the class ```QFT```.
    """

    def __init__(self, numberQubits, nameSpacePrefix=""):
        """
        The constructor of this class takes a the number of qubits and an optional name space prefix as
        parameters.

        Parameters
        ----------
        numberQubits : int
                      The number of qubits, which the InverseQFT acts on.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        InverseQFT : geqo.algorithms.InverseQFT
            An object of this class that corresponds to the InverseQFT.
        """
        self.qft = QFT(numberQubits, nameSpacePrefix)
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            "InverseQFT("
            + str(self.qft.numberQubits)
            + ', "'
            + self.nameSpacePrefix
            + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same number of qubits and the same name space prefix.
        False : else
        """
        if not isinstance(other, InverseQFT):
            return False
        return self.qft == other.qft and self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return an object of the class ```QFT``` with the same number of qubits and the same name space prefix.

        Returns
        -------
        QFT : geqo.algorithm.QFT
            A new object of this class, which corresponds to the QFT.
        """
        return self.qft

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of Hadamard and controlled phase gates. The sequence of gates
        correspond to the InverseQFT.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with Hadamard and controlled phase operations and the appropriate bits and qubits.
        """
        return self.qft.getEquivalentSequence().getInverse()

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this InverseQFT operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by this InverseQFT operation.
        """
        return self.qft.numberQubits

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by InverseQFT, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The InverseQFT can be decomposed into a sequence of Hadamard gates and controlled phase gates and a qubit reversal.
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


class PCCM(QuantumOperation):
    """The circuit for a phase-covariant cloning machine with one free parameter, which is
    the angle of a controlled rotation in its circuit representation.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```InversePCCM```.

    The circuit diagram can be found in figure 3 of
    T. Decker, M. Gallezot, S. F. Kerstan, A. Paesano, A. Ginter, W. Wormsbecher,
    "QKD as a Quantum Machine Learning task", arXiv:2410.01904
    """

    def __init__(self, name, nameSpacePrefix=""):
        """
        The constructor of this class takes a name and an optional name space prefix as
        parameters.

        Parameters
        ----------
        name : string
                    The name for the rotation angle inside the PCCM.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        PCCM : geqo.algorithms.PCCM
            An object of this class that corresponds to the PCCM.
        """
        self.name = name
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            'PCCM("' + str(self.name) + '", "' + self.nameSpacePrefix + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same name and name space prefix.
        False : else
        """
        if not isinstance(other, PCCM):
            return False
        return self.name == other.name and self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return an object of the class ```InversePCCM``` with the same name for the rotation angle and the same name space prefix.

        Returns
        -------
        InversePCCM : geqo.algorithm.InversePCCM
            A new object of this class, which corresponds to the inverse of the PCCM.
        """
        return InversePCCM(self.name, self.nameSpacePrefix)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of qubit swaps. The sequence of controlled and uncontrolled
        rotations correspond to the PCCM.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with controlled and uncontrolled rotation operations that correspond to the PCCM.
        """
        gate1 = Rx(self.nameSpacePrefix + "RX(π/2)")
        gate2 = Rx(self.nameSpacePrefix + "RX(π/2)")
        gate3 = QuantumControl(
            [1], Rx(self.nameSpacePrefix + "RX(" + str(self.name) + ")")
        )
        gate4 = QuantumControl([1], Rx(self.nameSpacePrefix + "RX(-π/2)"))
        gate5 = Rx(self.nameSpacePrefix + "RX(-π/2)")
        gate6 = Ry(self.nameSpacePrefix + "RY(-π/2)")
        seq = [
            (gate1, [0]),
            (gate2, [1]),
            (gate3, [0, 1]),
            (gate4, [1, 0]),
            (gate5, [0]),
            (gate6, [1]),
        ]
        s = Sequence([], [0, 1], seq)
        return s

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this PCCM operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by the PCCM.
        """
        return 2

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by the PCCM, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The PCCM can be decomposed into a sequence of rotation gates.
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


class InversePCCM(QuantumOperation):
    """This operation corresponds to the inverse of the phase-covariant cloning machine with
    a specified angle.

    The inverse can be obtained with ```getInverse()``` and it returns an object of type ```PCCM```.

    For more information, please refer to the documentation of the class ```PCCM```.
    """

    def __init__(self, name, nameSpacePrefix=""):
        """
        The constructor of this class takes a name and an optional name space prefix as
        parameters.

        Parameters
        ----------
        name : string
                    The name for the rotation angle inside the InversePCCM.
        nameSpacePrefix : string
                    The provided character string is prependet to all internally defined operations.

        Returns
        -------
        InversePCCM : geqo.algorithms.InversePCCM
            An object of this class that corresponds to the InversePCCM.
        """
        self.pccm = PCCM(name, nameSpacePrefix)
        self.nameSpacePrefix = nameSpacePrefix

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        string_representation = (
            'InversePCCM("' + str(self.pccm.name) + '", "' + self.nameSpacePrefix + '")'
        )
        return string_representation

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if it has the same name and name space prefix.
        False : else
        """
        if not isinstance(other, InversePCCM):
            return False
        return self.pccm == other.pccm and self.nameSpacePrefix == other.nameSpacePrefix

    def getInverse(self):
        """
        Return an object of the class ```PCCM``` with the same name for the rotation angle and the same name space prefix.

        Returns
        -------
        PCCM : geqo.algorithm.PCCM
            A new object of this class, which corresponds to the PCCM.
        """
        return self.pccm

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains a sequence of qubit swaps. The sequence of controlled and uncontrolled
        rotations correspond to the InversePCCM.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with controlled and uncontrolled rotation operations that correspond to the InversePCCM.
        """
        return self.pccm.getEquivalentSequence().getInverse()

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this InversePCCM operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by the InversePCCM.
        """
        return 2

    def getNumberClassicalBits(self):
        """
        Returns
        -------
        0 : int
            The number of classical bits, which are used by the InversePCCM, is zero.
        """
        return 0

    def hasDecomposition(self):
        """
        Returns
        -------
        True : Bool
            The InversePCCM can be decomposed into a sequence of rotation gates.
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


def controlledXGate(numberControls, namePrefix=""):
    """Implement an ```PauliX``` gate, which is controlled by multiple qubits. It is implemented with
    Toffoli gates and one ancilla qubit. This method creates an exponential number of Toffoli gates in
    the number of control qubits. This function needs one ancilla qubit, which is assumed to be
    the last one in the order.

    Parameters
    ----------
        numberControls : int
            The number of control qubits for this gate.
        namePrefix : string
            This character string is prepended to all internally used definitions.

    Returns
    -------
        toffoli : geqo.gates.multi_qubit_gates.Toffoli
            An object of the class ```Toffoli``` that is used in the decomposition. Its internal name space prefix is set to the given prefix.
        controlledXGateInternal : geqo.core.quantum_circuit.Sequence
            A sequence with gates that correspond to the controlled ```PauliX``` gate.
    """
    controls = list(range(numberControls))
    ancilla = [numberControls + 1]
    target = [numberControls]
    toffoli = Toffoli(namePrefix)
    return toffoli, controlledXGateInternal(controls, ancilla, target, toffoli)


def controlledXGateInternal(controls, ancilla, target, toffoli):
    """
    Internal function for the function ```controlledXGate```.

    Parameters
    ----------
    other : An object, which should be compared to this object.

    Returns
    -------
    a : int
    """
    seq = []

    if len(controls) > 3:
        buffer = controlledXGateInternal(
            controls[:-1], [controls[-1]], ancilla, toffoli
        )
        for b in buffer.gatesAndTargets:
            seq.append(b)
    else:
        seq.append(
            (
                QuantumControl([1] * (len(controls) - 1), PauliX()),
                controls[:-1] + ancilla,
            )
        )

    seq.append((toffoli, [controls[-1]] + ancilla + target))

    if len(controls) > 3:
        buffer = controlledXGateInternal(
            controls[:-1], [controls[-1]], ancilla, toffoli
        )
        for b in buffer.gatesAndTargets:
            seq.append(b)
    else:
        seq.append(
            (
                QuantumControl([1] * (len(controls) - 1), PauliX()),
                controls[:-1] + ancilla,
            )
        )

    seq.append((toffoli, [controls[-1]] + ancilla + target))

    return Sequence([], controls + target + ancilla, seq)
