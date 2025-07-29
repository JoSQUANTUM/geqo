from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation


class QuantumControl(QuantumOperation):
    """This class allows to turn a quantum operation into an operation with additional quantum controls. The
    argument ```onoff``` is a list of 0's and 1's corresponding to qubits that control the operations
    when in the state 0 and 1, respectively. The number of qubits of the resulting unitary is the number of qubits of
    the original gate plus the number of control qubits. The control qubits are ordered before the qubits of the
    original gate.

    For instance, ```QuantumControl([0,1],BasicGate("X", 2))``` defines a controlled version of
    the gate ```BasicGate("X", 2)``` on two qubits. The resulting gate operates on four qubits and the gate is
    executed when the first and second qubit are in the basis states 0 and 1, respectively.
    """

    def __init__(self, onoff, qop):
        """
        The constructor of this class takes a list of bit settings and an operator.

        Parameters
        ----------
        onoff : list( 0 | 1 )
            A list of 0 and 1 values. A ```0``` corresponds to a negative control of a qubit (the operation is performed if the
            basis state is 0) and ```1``` means a positive control qubit.
        qop : geqo.core.quantum_operation.QuantumOperation
            A quantum operation.

        Returns
        -------
        QuantumControl : geqo.operations.controls.QuantumControl
            An object of this class that corresponds to the controlled version of the provided gate.
        """
        self.onoff = onoff
        self.qop = qop

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "QuantumControl(" + str(self.onoff) + ", " + str(self.qop) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same list of qubit settings and the same operation.
        False : else
        """
        if not isinstance(other, QuantumControl):
            return False
        else:
            return self.onoff == other.onoff and self.qop == other.qop

    def getInverse(self, mustInvert=False):
        """
        Return an object of the same class, which corresponds to the inverse of the gate. The qubit setting is the same, but the operation is inverted, if possible. If no inverse exists, then an exception is raised.

        Returns
        -------
        QuantumControl : geqo.operations.controls.QuantumControl
            A new object of the class, which corresponds to the inverse gate. If no inverse exists, then an exception is raised.
        """
        return QuantumControl(self.onoff, self.qop.getInverse())

    def getEquivalentSequence(self):
        """Return an object of the class ```Sequence```, which corresponds to the controlled version of the gate.
        This function replaces a ```Sequence``` with control qubits into a ```Sequence``` of gates with the added control qubits.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with controlled operations and with the appropriate bits and qubits. Note that the number
            of qubits is extended by new qubits, which get new names, which are unique in the ```Sequence``` object.
        """
        originalSequence = self.qop.getEquivalentSequence()

        originalSequenceClassicalBits = originalSequence.bits
        originalSequenceQuantumBits = originalSequence.qubits

        # we need to prepend len(onoff) many new qubits; we have to find
        # unused names for it. We try out 0,.... until we find new ones.
        # The identifiers can be integers or character strings and we
        # have to add a new identifier of the same type.
        newQubits = []
        counter = 0
        while len(newQubits) < len(self.onoff):
            if (
                str(counter) not in newQubits
                and counter not in newQubits
                and str(counter) not in originalSequenceQuantumBits
                and counter not in originalSequenceQuantumBits
            ):
                if len(originalSequenceQuantumBits) > 0 and isinstance(
                    originalSequenceQuantumBits[0], int
                ):
                    newQubits.append(counter)  # qubits have integers as identifier
                else:
                    newQubits.append(str(counter))  # default case is string identifier

            counter = counter + 1

        newSequence = []
        for s in originalSequence.gatesAndTargets:
            if len(s) == 2:
                gate = s[0]
                targets = s[1]
                newGate = QuantumControl(self.onoff, gate)
                newSequence.append((newGate, newQubits + targets))
            elif len(s) == 3:
                gate = s[0]
                ctargets = s[1]
                s[2]
                newGate = QuantumControl(self.onoff, gate)
                newSequence.append((newGate, ctargets, newQubits + targets))
        return Sequence(
            originalSequenceClassicalBits,
            newQubits + originalSequenceQuantumBits,
            newSequence,
        )

    def hasDecomposition(self):
        """
        Returns
        -------
        hasDecomposition : Bool
            True or False depending on whether the provided operation has a decomposition or not.
        """
        return self.qop.hasDecomposition()

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation. Note that this is the sum of the qubits of the provided operation and the number of control qubits.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by the controlled operation.
        """
        return self.qop.getNumberQubits() + len(self.onoff)

    def getNumberClassicalBits(self):
        """
        Return the number of classical bits that are used by this operation. This is the same number as of the provided operation.

        Returns
        -------
        numberBits : int
            The number of classical bits, which are used by the controlled operation.
        """
        return self.qop.getNumberClassicalBits()

    def isUnitary(self):
        """
        Returns
        -------
        isUnitary : Bool
            Return True or False depending on whether the provided operation is unitary or not.
        """
        return self.qop.isUnitary()


class ClassicalControl(QuantumOperation):
    """This class allows to turn a quantum operation into an operation with additional classical controls. The
    quantum operation is specified by the argument ```qop```. The
    argument ```onoff``` is a list of 0's and 1's corresponding to bits that control the operations
    when set to 0 and 1, respectively. This operator acts on classical bits and qubits. The number of
    classical bits is the length of the argument ```onofff``` and the number of qubits is the same
    as for the quantum operation ```qop```.

    For instance, ```ClassicalControl([0,1], BasicGate("X", 2))``` defines a controlled version of
    the gate ```BasicGate("X", 2)``` on two qubits. The resulting gate operates on two classical bits and two qubits and
    the gate is executed when the two bits are set to 0 and 1, respectively.
    """

    def __init__(self, onoff, qop):
        """
        The constructor of this class takes a list of bit settings and an operator.

        Parameters
        ----------
        onoff : list( 0 | 1 )
            A list of 0 and 1 values. A ```0``` corresponds to a negative control of a classical bit (the operation is performed if the
            bit is 0) and ```1``` means a positive classical control bit.
        qop : geqo.core.quantum_operation.QuantumOperation
            A quantum operation.

        Returns
        -------
        ClassicalControl : geqo.operations.controls.ClassicalControl
            An object of this class that corresponds to the controlled version of the provided gate.
        """
        self.onoff = onoff
        self.qop = qop

    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return "ClassicalControl(" + str(self.onoff) + ", " + str(self.qop) + ")"

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if has the same list of bit settings and the same operation.
        False : else
        """
        if not isinstance(other, ClassicalControl):
            return False
        else:
            return self.onoff == other.onoff and self.qop == other.qop

    def getInverse(self):
        """
        Return an object of the same class, which corresponds to the inverse of the gate. The bit setting is the same, but the operation is inverted, if possible. If no inverse exists, then an exception is raised.

        Returns
        -------
        ClassicalControl : geqo.operations.controls.ClassicalControl
            A new object of the class, which corresponds to the inverse gate. If no inverse exists, then an exception is raised.
        """
        return ClassicalControl(self.onoff, self.qop.getInverse())

    def getEquivalentSequence(self):
        """Return an object of the class ```Sequence```, which corresponds to the controlled version of the gate.
        This function replaces a ```Sequence``` with control bits into a ```Sequence``` of gates with the added control bits.

        Returns
        -------

        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  with controlled operations and with the appropriate bits and qubits. Note that the number
            of bits is extended by new bits, which get new names, which are unique in the ```Sequence``` object.
        """
        originalSequence = self.qop.getEquivalentSequence()

        originalSequenceClassicalBits = originalSequence.bits
        originalSequenceQuantumBits = originalSequence.qubits

        newBits = []
        counter = 0
        while len(newBits) < len(self.onoff):
            if (
                str(counter) not in newBits
                and counter not in newBits
                and str(counter) not in originalSequenceClassicalBits
                and counter not in originalSequenceClassicalBits
            ):
                if len(originalSequenceClassicalBits) > 0 and isinstance(
                    originalSequenceClassicalBits[0], int
                ):
                    newBits.append(counter)  # qubits have integers as identifier
                else:
                    newBits.append(str(counter))  # default case is string identifier

            counter = counter + 1

        newSequence = []
        for s in originalSequence.gatesAndTargets:
            if len(s) == 2:
                gate = s[0]
                targets = s[1]
                newGate = ClassicalControl(self.onoff, gate)
                newSequence.append((newGate, newBits, targets))
            elif len(s) == 3:
                gate = s[0]
                ctargets = s[1]
                s[2]
                newGate = ClassicalControl(self.onoff, gate)
                newSequence.append((newGate, newBits + ctargets, targets))
        return Sequence(
            newBits + originalSequenceClassicalBits,
            originalSequenceQuantumBits,
            newSequence,
        )

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this operation. This is the same number as of the provided operation.

        Returns
        -------
        numberQubits : int
            The number of qubits, which are used by the controlled operation.
        """
        return self.qop.getNumberQubits()

    def getNumberClassicalBits(self):
        """
        Return the number of classical bits that are used by this operation. This is the sum of the classical bits of the provided operation and the control bits.

        Returns
        -------
        numberBits : int
            The number of classical bits, which are used by the controlled operation.
        """
        return self.qop.getNumberClassicalBits() + len(self.onoff)

    def hasDecomposition(self):
        """
        Returns
        -------
        hasDecomposition : Bool
            True or False depending on whether the provided operation has a decomposition or not.
        """
        return self.qop.hasDecomposition()

    def isUnitary(self):
        """
        Returns
        -------
        isUnitary : Bool
            Return True or False depending on whether the provided operation is unitary or not.
        """
        return self.qop.isUnitary()
