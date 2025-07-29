from geqo.core.quantum_circuit import Sequence
from geqo.gates.rotation_gates import (
    Rx,
    Ry,
    Rz,
    Rzz,
    InverseRx,
    InverseRy,
    InverseRz,
    InverseRzz,
)
from geqo.gates.fundamental_gates import CNOT


class TestRotation:
    def test_rx(self):
        name = "a"
        op = Rx("a")

        assert op.name == name
        assert str(op) == f'Rx("{name}")'
        assert op == Rx("a")
        assert not op == Ry("a")
        assert op.getInverse() == InverseRx("a")
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_inverse_rx(self):
        name = "a"
        op = InverseRx("a")

        assert op.name == name
        assert str(op) == f'InverseRx("{name}")'
        assert op == InverseRx("a")
        assert not op == Ry("a")
        assert op.getInverse() == Rx("a")
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_ry(self):
        name = "a"
        op = Ry("a")

        assert op.name == name
        assert str(op) == f'Ry("{name}")'
        assert op == Ry("a")
        assert not op == Rx("a")
        assert op.getInverse() == InverseRy("a")
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_inverse_ry(self):
        name = "a"
        op = InverseRy("a")

        assert op.name == name
        assert str(op) == f'InverseRy("{name}")'
        assert op == InverseRy("a")
        assert not op == Rx("a")
        assert op.getInverse() == Ry("a")
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_rz(self):
        name = "a"
        op = Rz("a")

        assert op.name == name
        assert str(op) == f'Rz("{name}")'
        assert op == Rz("a")
        assert not op == Ry("a")
        assert op.getInverse() == InverseRz("a")
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_inverse_rz(self):
        name = "a"
        op = InverseRz("a")

        assert op.name == name
        assert str(op) == f'InverseRz("{name}")'
        assert op == InverseRz("a")
        assert not op == Ry("a")
        assert op.getInverse() == Rz("a")
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_rzz(self):
        name = "a"
        op = Rzz("a")

        assert op.name == name
        assert str(op) == f'Rzz("{name}")'
        assert op == Rzz("a")
        assert not op == Ry("a")
        assert op.getInverse() == InverseRzz("a")
        ops = [(CNOT(), [0, 1]), (Rz("a"), [1]), (CNOT(), [0, 1])]
        seq = Sequence([], [0, 1], ops)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == 2
        assert op.getNumberClassicalBits() == 0
        assert op.hasDecomposition()
        assert op.isUnitary()

    def test_inverse_rzz(self):
        name = "a"
        op = InverseRzz("a")

        assert op.name == name
        assert str(op) == f'InverseRzz("{name}")'
        assert op == InverseRzz("a")
        assert not op == Ry("a")
        assert op.getInverse() == Rzz("a")
        ops = [(CNOT(), [0, 1]), (InverseRz("a"), [1]), (CNOT(), [0, 1])]
        seq = Sequence([], [0, 1], ops)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == 2
        assert op.getNumberClassicalBits() == 0
        assert op.hasDecomposition()
        assert op.isUnitary()
