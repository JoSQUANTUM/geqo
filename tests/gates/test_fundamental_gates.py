from geqo.gates.fundamental_gates import (
    CNOT,
    Hadamard,
    InversePhase,
    InverseSGate,
    PauliX,
    PauliY,
    PauliZ,
    Phase,
    SGate,
    SwapQubits,
)
from geqo.core.quantum_circuit import Sequence


class TestFundamentalGates:
    def test_pauli_gates(self):
        x = PauliX()
        y = PauliY()
        z = PauliZ()

        assert str(x) == "PauliX()"
        assert str(y) == "PauliY()"
        assert str(z) == "PauliZ()"

        assert x == PauliX()
        assert not x == PauliY()
        assert y == PauliY()
        assert not y == PauliX()
        assert z == PauliZ()
        assert not z == PauliX()

        assert x.getEquivalentSequence() == Sequence([], [0], [(x, [0])])
        assert y.getEquivalentSequence() == Sequence([], [0], [(y, [0])])
        assert z.getEquivalentSequence() == Sequence([], [0], [(z, [0])])

        assert x.getNumberQubits() == 1
        assert y.getNumberQubits() == 1
        assert z.getNumberQubits() == 1

        assert x.getNumberClassicalBits() == 0
        assert y.getNumberClassicalBits() == 0
        assert z.getNumberClassicalBits() == 0

        assert not x.hasDecomposition()
        assert not y.hasDecomposition()
        assert not z.hasDecomposition()

        assert x.isUnitary()
        assert y.isUnitary()
        assert z.isUnitary()

    def test_hadamard_gate(self):
        h = Hadamard()
        assert str(h) == "Hadamard()"
        assert h == Hadamard()
        assert not h == PauliX()
        assert h.getEquivalentSequence() == Sequence([], [0], [(h, [0])])
        assert h.getNumberClassicalBits() == 0
        assert h.getNumberQubits() == 1
        assert not h.hasDecomposition()
        assert h.isUnitary()

    def test_phase_gates(self):
        p = Phase("test")
        ip = InversePhase("test")

        assert str(p) == 'Phase("test")'
        assert str(ip) == 'InversePhase("test")'

        assert p == Phase("test")
        assert not p == InversePhase("test")
        assert ip == InversePhase("test")
        assert not ip == Phase("test")

        assert p.getEquivalentSequence() == Sequence([], [0], [(p, [0])])
        assert ip.getEquivalentSequence() == Sequence([], [0], [(ip, [0])])

        assert p.getNumberClassicalBits() == 0
        assert ip.getNumberClassicalBits() == 0

        assert p.getNumberQubits() == 1
        assert ip.getNumberQubits() == 1

        assert p.isUnitary()
        assert ip.isUnitary()

        assert str(p.getInverse()) == str(ip)
        assert str(ip.getInverse()) == str(p)

        assert not p.hasDecomposition()
        assert not ip.hasDecomposition()

    def test_cnot_gate(self):
        cnot = CNOT()
        assert str(cnot) == "CNOT()"
        assert cnot == CNOT()
        assert not cnot == Hadamard()
        assert cnot.getEquivalentSequence() == Sequence([], [0, 1], [(cnot, [0, 1])])
        assert cnot.getNumberClassicalBits() == 0
        assert cnot.getNumberQubits() == 2
        assert cnot.isUnitary()
        assert not cnot.hasDecomposition()

    def test_s_gates(self):
        s = SGate()
        inv_s = InverseSGate()

        assert str(s) == "SGate()"
        assert str(inv_s) == "InverseSGate()"

        assert s == SGate()
        assert not s == InverseSGate()
        assert inv_s == InverseSGate()
        assert not inv_s == SGate()

        assert s.getEquivalentSequence() == Sequence([], [0], [(s, [0])])
        assert inv_s.getEquivalentSequence() == Sequence([], [0], [(inv_s, [0])])

        assert s.getNumberClassicalBits() == 0
        assert inv_s.getNumberClassicalBits() == 0
        assert s.getNumberQubits() == 1
        assert inv_s.getNumberQubits() == 1

        assert s.isUnitary()
        assert inv_s.isUnitary()

        assert str(s.getInverse()) == str(inv_s)
        assert str(inv_s.getInverse()) == str(s)

        assert not s.hasDecomposition()
        assert not inv_s.hasDecomposition()

    def test_swap_gate(self):
        swap = SwapQubits()
        assert str(swap) == "SwapQubits()"
        assert swap == SwapQubits()
        assert not swap == PauliX()
        assert swap.getEquivalentSequence() == Sequence([], [0, 1], [(swap, [0, 1])])
        assert swap.getNumberClassicalBits() == 0
        assert swap.getNumberQubits() == 2
        assert swap.getInverse() == swap
        assert swap.isUnitary()
        assert not swap.hasDecomposition()
