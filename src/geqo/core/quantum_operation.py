import abc


class QuantumOperation(metaclass=abc.ABCMeta):
    """Abstract base class for all quantum operations. These operations
    can be unitary and non-unitary and they can act on classical bits and qubits.
    """

    @abc.abstractmethod
    def __init__(self):
        """
        The constructor of ```QuantumOperation``` objects. The parameters depend on the specific sub-classes.
        """
        pass

    @abc.abstractmethod
    def __repr__(self):
        """
        Return a representation of the object as character string.
        """
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        """
        Compare the object of a sub-class with another object.
        """
        pass

    @abc.abstractmethod
    def getInverse(self):
        """
        Return the inverse of a sub-class, if the inverse exists. If no inverse exists, then raise an exception.
        """
        pass

    @abc.abstractmethod
    def getEquivalentSequence(self):
        """
        Return an object of the class ```Sequence```, which corresponds to a sub-class, if a corresponing object is defined.
        """
        pass

    @abc.abstractmethod
    def isUnitary(self):
        """
        Return True or False depending on the unitary of a sub-class.
        """
        pass

    @abc.abstractmethod
    def hasDecomposition(self):
        """
        Return True or False depending on whether a replacement ```Sequence``` object is defined for the method ```getEquivalentSequence```.
        """
        pass

    @abc.abstractmethod
    def getNumberQubits(self):
        """
        Get the number of qubits on which the sub-class operations.
        """
        pass

    @abc.abstractmethod
    def getNumberClassicalBits(self):
        """
        Get the number of classical bits on which the sub-class operations.
        """
        pass
