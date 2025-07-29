from geqo.operations.controls import QuantumControl, ClassicalControl
from geqo.gates.fundamental_gates import Hadamard
from geqo.core.quantum_circuit import Sequence


class TestControls:
    def test_quantum_control(self):
        onoff = [1, 0]
        qop = Hadamard()
        op = QuantumControl(onoff, qop)

        assert op.onoff == onoff
        assert op.qop == qop
        assert str(op) == "QuantumControl(" + str(onoff) + ", " + str(qop) + ")"
        assert op == QuantumControl([1, 0], Hadamard())
        assert not op == Hadamard()
        assert op.getInverse() == op
        assert op.hasDecomposition() == qop.hasDecomposition()
        assert op.getNumberQubits() == 3
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary
        assert op.getEquivalentSequence() == Sequence(
            [], [1, 2, 0], [(QuantumControl([1, 0], Hadamard()), [1, 2, 0])]
        )

    def test_classical_control(self):
        onoff = [1, 0]
        qop = Hadamard()
        op = ClassicalControl(onoff, qop)

        assert op.onoff == onoff
        assert op.qop == qop
        assert str(op) == "ClassicalControl(" + str(onoff) + ", " + str(qop) + ")"
        assert op == ClassicalControl([1, 0], Hadamard())
        assert not op == Hadamard()
        assert op.getInverse() == op
        assert op.hasDecomposition() == qop.hasDecomposition()
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 2
        assert op.isUnitary() == qop.isUnitary()
        assert op.getEquivalentSequence() == Sequence(
            ["0", "1"], [0], [(op, ["0", "1"], [0])]
        )
