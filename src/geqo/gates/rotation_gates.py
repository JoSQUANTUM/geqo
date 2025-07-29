from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.gates.fundamental_gates import CNOT


class Rx(QuantumOperation):
    """Rotation about X axis in Bloch sphere."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        Rx : geqo.gates.rotation_gates.Rx
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'Rx("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, Rx):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```InverseRx``` with the same name for the angle.

        Returns
        -------
        InverseRx : geqo.gates.rotation_gates.InverseRx
            A new object of the class ```InverseRx```, which corresponds to the inverse operation.
        """
        return InverseRx(self.name)

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
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this rotation gate.
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
            This rotation on a single qubit is considered to be as a non-decomposable operation.
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


class InverseRx(QuantumOperation):
    """Inverse rotation about X axis."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        InverseRx : geqo.gates.rotation_gates.InverseRx
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'InverseRx("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, InverseRx):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```Rx``` with the same name for the angle.

        Returns
        -------
        Rx : geqo.gates.rotation_gates.Rx
            A new object of the class ```Rx```, which corresponds to the inverse operation.
        """
        return Rx(self.name)

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
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this rotation gate.
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
            This rotation on a single qubit is considered to be as a non-decomposable operation.
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


class Ry(QuantumOperation):
    """Rotation about Y axis in Bloch sphere."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        Ry : geqo.gates.rotation_gates.Ry
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'Ry("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, Ry):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```InverseRy``` with the same name for the angle.

        Returns
        -------
        InverseRy : geqo.gates.rotation_gates.InverseRy
            A new object of the class ```InverseRy```, which corresponds to the inverse operation.
        """
        return InverseRy(self.name)

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
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this rotation gate.
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
            This rotation on a single qubit is considered to be as a non-decomposable operation.
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


class InverseRy(QuantumOperation):
    """Inverse rotation about Y axis."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        InverseRx : geqo.gates.rotation_gates.InverseRx
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'InverseRy("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, InverseRy):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```Ry``` with the same name for the angle.

        Returns
        -------
        Ry : geqo.gates.rotation_gates.Ry
            A new object of the class ```Ry```, which corresponds to the inverse operation.
        """
        return Ry(self.name)

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
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this rotation gate.
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
            This rotation on a single qubit is considered to be as a non-decomposable operation.
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


class Rz(QuantumOperation):
    """Rotation about Z axis in Bloch sphere."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        Rz : geqo.gates.rotation_gates.Rz
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'Rz("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, Rz):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```InverseRz``` with the same name for the angle.

        Returns
        -------
        InverseRz : geqo.gates.rotation_gates.InverseRzz
            A new object of the class ```InverseRz```, which corresponds to the inverse operation.
        """
        return InverseRz(self.name)

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
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this rotation gate.
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
            This rotation on a single qubit is considered to be as a non-decomposable operation.
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


class InverseRz(QuantumOperation):
    """Inverse rotation about Z axis."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        InverseRz : geqo.gates.rotation_gates.InverseRz
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'InverseRz("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, InverseRz):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```Rz``` with the same name for the angle.

        Returns
        -------
        Rz : geqo.gates.rotation_gates.Rz
            A new object of the class ```Rz```, which corresponds to the inverse operation.
        """
        return Rz(self.name)

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
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        1 : int
            The number of qubits, which are used by this rotation gate.
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
            This rotation on a single qubit is considered to be as a non-decomposable operation.
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


class Rzz(QuantumOperation):
    """ZZ interaction between two qubits."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        Rzz : geqo.gates.rotation_gates.Rzz
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'Rzz("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, Rzz):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```InverseRzz``` with the same name for the angle.

        Returns
        -------
        InverseRzz : geqo.gates.rotation_gates.InverseRzz
            A new object of the class ```InverseRzz```, which corresponds to the inverse operation.
        """
        return InverseRzz(self.name)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains several operations that correspond to
        this gate.

        Returns
        -------
        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        cx = CNOT()
        rz = Rz(self.name)
        seq = [(cx, [0, 1]), (rz, [1]), (cx, [0, 1])]
        return Sequence([], [0, 1], seq)

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by this rotation gate.
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
        True : Bool
            This two-qubit operation can be decomposed into a sequence of two ```CNOT``` and one ```Rz``` gate.
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


class InverseRzz(QuantumOperation):
    """Inverse ZZ interaction between two qubits."""

    def __init__(self, name):
        """
        The constructor of this class takes a name as parameter. This name denotes the rotation angle.

        Parameters
        ----------
        name : String
            The name of the angle of this rotation.

        Returns
        -------
        InverseRzz : geqo.gates.rotation_gates.InverseRzz
            An object of this class that corresponds to the rotation with the specified rotation.
        """
        self.name = name

    def __repr__(self):
        """
        Returns a representation of the object as character string.
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f'InverseRzz("{self.name}")'

    def __eq__(self, other):
        """
        Comparator with other objects.

        Parameters
        ----------
        other : An object, which should be compared to this object.

        Returns
        -------
        True : If the provided object is of the same type and if the angle have the same names.
        False : else
        """
        if not isinstance(other, InverseRzz):
            return False
        else:
            return self.name == other.name

    def getInverse(self):
        """
        Return an object of the class ```Rzz``` with the same name for the angle.

        Returns
        -------
        Rzz : geqo.gates.rotation_gates.Rzz
            A new object of the class ```Rzz```, which corresponds to the inverse operation.
        """
        return Rzz(self.name)

    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which contains several operations that correspond to
        this gate.

        Returns
        -------
        sequence : geqo.core.Sequence
            An object of the class ```Sequence```  without operations, but with the appropriate bits and qubits.
        """
        return Rzz(self.name).getEquivalentSequence().getInverse()

    def getNumberQubits(self):
        """
        Return the number of qubits that are used by this permuation operation.

        Returns
        -------
        2 : int
            The number of qubits, which are used by this rotation gate.
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
        True : Bool
            This two-qubit operation can be decomposed into a sequence of two ```CNOT``` and one ```InverseRz``` gate.
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
