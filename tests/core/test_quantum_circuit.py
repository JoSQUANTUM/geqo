from geqo.core.quantum_circuit import Sequence
from geqo.gates.fundamental_gates import CNOT, Hadamard


class TestQuantumCircuit:
    def test_basic_circuit(self):
        # Test basic circuit creation
        circ = Sequence([0], [0, 1], [(Hadamard(), [0]), (CNOT(), [0, 1])])
        assert len(circ.bits) == 1
        assert len(circ.qubits) == 2
        assert len(circ.gatesAndTargets) == 2
        assert circ.getNumberQubits() == 2
        assert circ.getNumberClassicalBits() == 1
        assert circ.isUnitary()
        assert not circ == Hadamard()

    def test_named_circuit(self):
        # Test named circuit
        circ = Sequence([], [0], [(Hadamard(), [0])], "TestCircuit")
        assert circ.name == "TestCircuit"
        assert "TestCircuit" in str(circ)

    def test_circuit_inverse(self):
        # Test circuit inversion
        circ = Sequence([], [0, 1], [(Hadamard(), [0]), (CNOT(), [0, 1])])
        inv_circ = circ.getInverse()

        # Verify inverse has operations in reverse order
        assert len(inv_circ.gatesAndTargets) == 2
        assert isinstance(inv_circ.gatesAndTargets[0][0], CNOT)
        assert isinstance(inv_circ.gatesAndTargets[1][0], Hadamard)

    def test_non_unitary_circuit(self):
        # Test with measurement operation (non-unitary)
        from geqo.operations.measurement import Measure

        circ = Sequence([0], [0], [(Measure(1), [0])])
        assert not circ.isUnitary()

    def test_operation_ordering(self):
        # Verify operation ordering is preserved
        ops = [(Hadamard(), [0]), (CNOT(), [0, 1]), (Hadamard(), [1])]
        circ = Sequence([], [0, 1], ops)
        assert len(circ.gatesAndTargets) == 3
        assert isinstance(circ.gatesAndTargets[0][0], Hadamard)
        assert isinstance(circ.gatesAndTargets[1][0], CNOT)
        assert isinstance(circ.gatesAndTargets[2][0], Hadamard)
