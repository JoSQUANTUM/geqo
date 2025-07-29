from geqo.gates.fundamental_gates import CNOT, Hadamard, Phase
from geqo.gates.multi_qubit_gates import Toffoli


class TestMultiQubitGates:
    def test_toffoli_basic_properties(self):
        toff = Toffoli()
        assert str(toff) == 'Toffoli("")'
        assert toff == Toffoli()
        assert not toff == CNOT()
        assert toff.getNumberQubits() == 3
        assert toff.getNumberClassicalBits() == 0
        assert toff.isUnitary()
        assert toff.hasDecomposition()

    def test_toffoli_namespace(self):
        toff = Toffoli("test.")
        assert str(toff) == 'Toffoli("test.")'

    def test_toffoli_inverse(self):
        toff = Toffoli()
        assert toff.getInverse() == toff  # Toffoli is self-inverse

    def test_toffoli_decomposition(self):
        toff = Toffoli()
        seq = toff.getEquivalentSequence()

        # Verify sequence structure
        assert len(seq.gatesAndTargets) == 15
        assert seq.qubits == [0, 1, 2]

        # Spot check some decomposition components
        assert isinstance(seq.gatesAndTargets[0][0], Hadamard)
        assert isinstance(seq.gatesAndTargets[1][0], CNOT)
        assert isinstance(seq.gatesAndTargets[2][0], Phase)
