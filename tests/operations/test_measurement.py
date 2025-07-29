import pytest

from geqo.operations.measurement import DropQubits, Measure
from geqo.core.quantum_circuit import Sequence


class TestMeasurementOperations:
    def test_measure_operation(self):
        # Test basic measurement operation
        m = Measure(2)
        assert str(m) == "Measure(2)"
        assert not m == DropQubits(2)
        assert m.getNumberQubits() == 2
        assert m.getNumberClassicalBits() == 2
        assert not m.isUnitary()
        assert m.getEquivalentSequence() == Sequence(
            [0, 1], [0, 1], [(m, [0, 1], [0, 1])]
        )

        # Test that inverse raises exception
        with pytest.raises(Exception):
            m.getInverse()

    def test_drop_qubits_operation(self):
        # Test drop qubits operation
        d = DropQubits(1)
        assert str(d) == "DropQubits(1)"
        assert not d == Measure(1)
        assert d == DropQubits(1)
        assert d.getNumberQubits() == 1
        assert d.getNumberClassicalBits() == 0
        assert not d.isUnitary()
        assert d.getEquivalentSequence() == Sequence([], [0], [(d, [0])])

        # Test that inverse raises exception
        with pytest.raises(Exception):
            d.getInverse()

    def test_varying_qubit_counts(self):
        # Test with different qubit counts
        for n in [1, 2, 3]:
            m = Measure(n)
            assert m.getNumberQubits() == n
            assert m.getNumberClassicalBits() == n

            d = DropQubits(n)
            assert d.getNumberQubits() == n
            assert d.getNumberClassicalBits() == 0
