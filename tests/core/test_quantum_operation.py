import pytest

from geqo.core.quantum_operation import QuantumOperation


class TestQuantumOperation:
    def test_abstract_methods(self):
        # Verify all required abstract methods exist
        assert hasattr(QuantumOperation, "__init__")
        assert hasattr(QuantumOperation, "__repr__")
        assert hasattr(QuantumOperation, "__eq__")
        assert hasattr(QuantumOperation, "getInverse")
        assert hasattr(QuantumOperation, "getEquivalentSequence")
        assert hasattr(QuantumOperation, "isUnitary")
        assert hasattr(QuantumOperation, "hasDecomposition")
        assert hasattr(QuantumOperation, "getNumberQubits")
        assert hasattr(QuantumOperation, "getNumberClassicalBits")

    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            QuantumOperation()

    def test_concrete_implementation(self):
        # Test a mock implementation
        class MockOperation(QuantumOperation):
            def __init__(self):
                super().__init__()

            def __repr__(self):
                return "MockOp"

            def __eq__(self, other):
                if not isinstance(other, MockOperation):
                    return False
                else:
                    return True

            def getInverse(self):
                return self

            def getEquivalentSequence(self):
                return None

            def isUnitary(self):
                return True

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        class MockOperation2(QuantumOperation):
            def __init__(self):
                super().__init__()

            def __repr__(self):
                return "MockOp2"

            def __eq__(self, other):
                if not isinstance(other, MockOperation2):
                    return False
                else:
                    return True

            def getInverse(self):
                return self

            def getEquivalentSequence(self):
                return None

            def isUnitary(self):
                return True

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        op = MockOperation()
        clone_op = MockOperation()
        diff_op = MockOperation2()
        assert str(op) == "MockOp"
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == op
        assert op.isUnitary()
        assert not op.hasDecomposition()
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
