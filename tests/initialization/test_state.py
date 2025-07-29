from geqo.core.quantum_circuit import Sequence
from geqo.initialization.state import SetBits, SetQubits, SetDensityMatrix
import pytest


class TestIntialization:
    def test_setbits(self):
        name = "sb"
        num_bits = 1
        op = SetBits(name, num_bits)

        assert op.name == name
        assert op.numberBits == num_bits
        assert str(op) == 'SetBits("' + name + '", ' + str(num_bits) + ")"
        assert op == SetBits("sb", 1)
        assert not op == SetQubits("sq", 1)
        with pytest.raises(Exception) as exc_info:
            op.getInverse()
        exc = exc_info.value
        assert exc.args[0] == "SetBits has no inverse"

        assert op.getEquivalentSequence() == Sequence(
            [0], [], [(SetBits("sb", 1), [0])]
        )
        assert op.getNumberQubits() == 0
        assert op.getNumberClassicalBits() == 1
        assert not op.hasDecomposition()
        assert not op.isUnitary()

    def test_setqubits(self):
        name = "sq"
        num_qubits = 1
        op = SetQubits(name, num_qubits)

        assert op.name == name
        assert op.numberQubits == num_qubits
        assert str(op) == 'SetQubits("' + name + '", ' + str(num_qubits) + ")"
        assert op == SetQubits("sq", 1)
        assert not op == SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            op.getInverse()
        exc = exc_info.value
        assert exc.args[0] == "SetQubits has no inverse"

        assert op.getEquivalentSequence() == Sequence(
            [], [0], [(SetQubits("sq", 1), [0])]
        )
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert not op.isUnitary()

    def test_setdensitymatrix(self):
        name = "sd"
        num_qubits = 1
        op = SetDensityMatrix(name, num_qubits)

        assert op.name == name
        assert op.numberQubits == num_qubits
        assert str(op) == 'SetDensityMatrix("' + name + '", ' + str(num_qubits) + ")"
        assert op == SetDensityMatrix("sd", 1)
        assert not op == SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            op.getInverse()
        exc = exc_info.value
        assert exc.args[0] == "SetDensityMatrix has no inverse"

        assert op.getEquivalentSequence() == Sequence(
            [], [0], [(SetDensityMatrix("sd", 1), [0])]
        )
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert not op.isUnitary()
