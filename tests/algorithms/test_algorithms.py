from geqo.algorithms.algorithms import (
    PermuteQubits,
    QubitReversal,
    QFT,
    InverseQFT,
    PCCM,
    InversePCCM,
)
from geqo.core.quantum_circuit import Sequence
from geqo.gates.fundamental_gates import SwapQubits, Hadamard, Phase, InversePhase
from geqo.gates.rotation_gates import Rx, Ry, InverseRx, InverseRy
from geqo.operations.controls import QuantumControl


class TestAlgorithms:
    def test_permute_qubits(self):
        order = [2, 3, 0, 1]
        op = PermuteQubits(order)
        clone_op = PermuteQubits(order)
        diff_op = Hadamard()
        inv_order = [order.index(x) for x in range(len(order))]
        seq = Sequence([], [*range(len(order))], [(op, [*range(len(order))])])

        assert op.targetOrder == order
        assert str(op) == "PermuteQubits(" + str(order) + ")"
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == PermuteQubits(inv_order)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == len(order)
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary()
        assert not op.hasDecomposition()

    def test_qubit_reversal(self):
        num_qubits = 5
        op = QubitReversal(num_qubits)
        clone_op = QubitReversal(num_qubits)
        diff_op = Hadamard()
        op_and_targets = [
            (SwapQubits(), [i, num_qubits - i - 1]) for i in range(num_qubits // 2)
        ]
        seq = Sequence([], [*range(num_qubits)], op_and_targets)

        assert op.numberQubits == num_qubits
        assert str(op) == "QubitReversal(" + str(num_qubits) + ")"
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == op
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == num_qubits
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary()
        assert op.hasDecomposition()

    def test_QFT(self):
        num_qubits = 5
        prefix = "pre"
        op = QFT(num_qubits, prefix)
        clone_op = QFT(num_qubits, prefix)
        diff_op = Hadamard()
        op_and_targets = []
        for i in range(num_qubits):
            op_and_targets.append((Hadamard(), [i]))
            for j in range(1, num_qubits - i):
                op_and_targets.append(
                    (
                        QuantumControl([1], Phase(prefix + "Ph" + str(j))),
                        [i + j, i],
                    )
                )
        op_and_targets.append((QubitReversal(num_qubits), list(range(num_qubits))))
        seq = Sequence([], list(range(num_qubits)), op_and_targets)

        assert op.numberQubits == num_qubits
        assert op.nameSpacePrefix == prefix
        assert str(op) == "QFT(" + str(num_qubits) + ', "' + prefix + '")'
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == InverseQFT(num_qubits, prefix)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == num_qubits
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary()
        assert op.hasDecomposition()

    def test_inverse_QFT(self):
        num_qubits = 5
        prefix = "pre"
        op = InverseQFT(num_qubits, prefix)
        clone_op = InverseQFT(num_qubits, prefix)
        diff_op = Hadamard()
        op_and_targets = []
        op_and_targets.append((QubitReversal(num_qubits), list(range(num_qubits))))
        for i in reversed(range(num_qubits)):
            for j in reversed(range(1, num_qubits - i)):
                op_and_targets.append(
                    (
                        QuantumControl([1], InversePhase(prefix + "Ph" + str(j))),
                        [i + j, i],
                    )
                )
            op_and_targets.append((Hadamard(), [i]))

        seq = Sequence([], list(range(num_qubits)), op_and_targets)

        assert op.qft == QFT(num_qubits, prefix)
        assert op.nameSpacePrefix == prefix
        assert str(op) == "InverseQFT(" + str(num_qubits) + ', "' + prefix + '")'
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == QFT(num_qubits, prefix)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == num_qubits
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary()
        assert op.hasDecomposition()

    def test_PCCM(self):
        name = "a"
        prefix = "pre"
        op = PCCM(name, prefix)
        clone_op = PCCM(name, prefix)
        diff_op = Hadamard()
        gate1 = Rx(prefix + "RX(π/2)")
        gate2 = Rx(prefix + "RX(π/2)")
        gate3 = QuantumControl([1], Rx(prefix + "RX(" + name + ")"))
        gate4 = QuantumControl([1], Rx(prefix + "RX(-π/2)"))
        gate5 = Rx(prefix + "RX(-π/2)")
        gate6 = Ry(prefix + "RY(-π/2)")
        op_and_targets = [
            (gate1, [0]),
            (gate2, [1]),
            (gate3, [0, 1]),
            (gate4, [1, 0]),
            (gate5, [0]),
            (gate6, [1]),
        ]
        seq = Sequence([], [0, 1], op_and_targets)

        assert op.name == name
        assert op.nameSpacePrefix == prefix
        assert str(op) == 'PCCM("' + name + '", "' + prefix + '")'
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == InversePCCM(name, prefix)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == 2
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary()
        assert op.hasDecomposition()

    def test_inverse_PCCM(self):
        name = "a"
        prefix = "pre"
        op = InversePCCM(name, prefix)
        clone_op = InversePCCM(name, prefix)
        diff_op = Hadamard()
        gate1 = InverseRx(prefix + "RX(π/2)")
        gate2 = InverseRx(prefix + "RX(π/2)")
        gate3 = QuantumControl([1], InverseRx(prefix + "RX(" + name + ")"))
        gate4 = QuantumControl([1], InverseRx(prefix + "RX(-π/2)"))
        gate5 = InverseRx(prefix + "RX(-π/2)")
        gate6 = InverseRy(prefix + "RY(-π/2)")
        op_and_targets = [
            (gate6, [1]),
            (gate5, [0]),
            (gate4, [1, 0]),
            (gate3, [0, 1]),
            (gate2, [1]),
            (gate1, [0]),
        ]
        seq = Sequence([], [0, 1], op_and_targets)

        assert op.pccm == PCCM(name, prefix)
        assert op.nameSpacePrefix == prefix
        assert str(op) == 'InversePCCM("' + name + '", "' + prefix + '")'
        assert op == clone_op
        assert op != diff_op
        assert op.getInverse() == PCCM(name, prefix)
        assert op.getEquivalentSequence() == seq
        assert op.getNumberQubits() == 2
        assert op.getNumberClassicalBits() == 0
        assert op.isUnitary()
        assert op.hasDecomposition()
