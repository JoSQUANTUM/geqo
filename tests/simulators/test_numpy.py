import numpy as np
import pytest

from geqo.algorithms.algorithms import (
    PCCM,
    QFT,
    InversePCCM,
    InverseQFT,
    PermuteQubits,
    QubitReversal,
)
from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
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
from geqo.gates.multi_qubit_gates import Toffoli
from geqo.gates.rotation_gates import (
    InverseRx,
    InverseRy,
    InverseRz,
    InverseRzz,
    Rx,
    Ry,
    Rz,
    Rzz,
)
from geqo.initialization.state import SetBits, SetDensityMatrix, SetQubits
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.operations.measurement import DropQubits, Measure
from geqo.simulators.numpy.implementation import simulatorStatevectorNumpy

gates = [
    BasicGate("b", 1),
    InverseBasicGate("b", 1),
    PauliX(),
    PauliY(),
    PauliZ(),
    SwapQubits(),
    Hadamard(),
    Phase("a"),
    InversePhase("a"),
    CNOT(),
    SGate(),
    InverseSGate(),
    Rx("a"),
    Ry("a"),
    Rz("a"),
    Rzz("a"),
    InverseRx("a"),
    InverseRy("a"),
    InverseRz("a"),
    InverseRzz("a"),
    QuantumControl([0], Ry("a")),
    PermuteQubits([1, 0]),
    QubitReversal(2),
]

op = []
for g in gates:
    if g.getNumberQubits() == 1:
        op.extend([(g, [0]), (g.getInverse(), [0])])
    else:
        op.extend([(g, [0, 1]), (g.getInverse(), [0, 1])])

identity_seq = Sequence([], [0, 1], op)


class TestNumpySimulator:
    def test_statevector_simulator(self):
        nqubits = 3
        ncbits = 2
        sim = simulatorStatevectorNumpy(ncbits, nqubits)
        state = np.zeros(shape=(2**nqubits, 1), dtype=np.complex128)
        state[0, 0] = 1.0 + 0 * 1j

        assert sim.numberBits == ncbits
        assert sim.numberQubits == nqubits
        assert np.array_equal(sim.state, state)
        assert sim.measurementResult == {}
        assert not sim.measurementHappened
        assert sim.values == {}
        assert sim.classicalBits == [0] * ncbits
        assert (
            str(sim)
            == "simulatorStatevectorNumpy(" + str(ncbits) + ", " + str(nqubits) + ")"
        )

        with pytest.raises(
            NotImplementedError,
            match="Too many qubits, limit is 32",
        ):
            sim_fail = simulatorStatevectorNumpy(33, 33)
            sim_fail.numberBits = 0

        sim.setValue("a", 1.23)
        # b = 2.34
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "Ph1": np.pi / 2,
            "RX(π/2)": np.pi / 2,
            "RX(-π/2)": -np.pi / 2,
            "RY(-π/2)": -np.pi / 2,
            "RX(a)": 1.23,
            # "RX(b)": b,
            "S.Pi/4": np.pi / 4,
            "-S.Pi/4": -np.pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

    def test_statevector_simulator_unitary(self):
        sim = simulatorStatevectorNumpy(0, 2)
        sim.setValue("a", 0.1)
        matrix = np.array([[1, 0], [0, 1]])
        sim.setValue("b", matrix)
        sim.apply(identity_seq, [0, 1])
        state = sim.state
        expect = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128).reshape(4, 1)
        assert np.allclose(expect, state)

    def test_statevector_simulator_non_unitary(self):
        # test Measure
        sim = simulatorStatevectorNumpy(2, 2)
        with pytest.raises(
            ValueError,
            match="Number of targets does not match number of measured qubits",
        ):
            sim.apply(Measure(3), [0, 1], [0, 1])
        # with pytest.raises(Exception) as exc_info:
        #    sim.apply(Measure(2), [0, 1], [0, 1])
        # exc = exc_info.value
        # assert exc.args[0] == "quantum control of measurement not supported"

        sim.apply(Hadamard(), [0])
        sim.apply(Measure(2), [0, 1], [0, 1])

        assert sim.measurementHappened
        assert np.allclose(sim.measurementResult[(0, 0)], 0.5)
        assert np.allclose(sim.measurementResult[(1, 0)], 0.5)

        # test SetBits
        setbit = SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(setbit, [0], [0])
        exc = exc_info.value
        assert exc.args[0] == "no more operation allowed after measurement"

        sim = sim = simulatorStatevectorNumpy(2, 2)
        with pytest.raises(
            ValueError,
            match=f'Bit values "{setbit.name}" not found',
        ):
            sim.apply(setbit, [0], [0])

        sim.setValue("sb", [1])
        with pytest.raises(
            ValueError,
            match="wrong number of bits in definition for SetBits",
        ):
            sim.apply(setbit, [0], [0, 1])

        sim.apply(setbit, [0], [0])
        assert sim.classicalBits == [1, 0]

        # test SetQubits
        setqubits = SetQubits("sq", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(setqubits, [0])
        exc = exc_info.value
        assert exc.args[0] == "cannot set qubits in statevector simulations"

        # test DropQubits
        dropqubits = DropQubits(1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(dropqubits, [0])
        exc = exc_info.value
        assert exc.args[0] == "cannot drop qubits in statevector simulations"

        # test SetDensityMatrix
        setden = SetDensityMatrix("sd", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(setden, [0])
        exc = exc_info.value
        assert exc.args[0] == "cannot set density matrix in statevector simulations"

        # test ClassicalControl
        setden = ClassicalControl([1], Hadamard())
        with pytest.raises(Exception) as exc_info:
            sim.apply(setden, [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0] == "cannot perform ClassicalControl in statevector simulations"
        )

        # test unknown operation
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
                return False

            def hasDecomposition(self):
                return False

            def getNumberQubits(self):
                return 1

            def getNumberClassicalBits(self):
                return 0

        op = MockOperation()
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert exc.args[0] == "gate not supported:"
        assert exc.args[1] == str(op)

    def test_edge_cases(self):
        sim = simulatorStatevectorNumpy(2, 2)
        # seq = Sequence([0, 1], [0, 1], [(Hadamard(), [0], [0], [0])])
        # with pytest.raises(Exception) as exc_info:
        #    sim.apply(seq, [0, 1], [0, 1])
        # exc = exc_info.value
        # assert exc.args[0] == "input sequence is invalid"

        # test basicgate
        op = BasicGate("a", 1)
        # matrix = np.array([[1, 0], [0, 1]])
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0])
        exc = exc_info.value
        assert (
            exc.args[0] == "Parameter " + str(op.name) + " in BasicGate is undefined."
        )

        """with pytest.raises(
            ValueError,
            match=re.escape(f"Gate {op} not found"),
        ):
            sim.apply(op, [0])"""

        """with pytest.raises(
            ValueError,
            match=re.escape("Wrong number of targets"),
        ):
            sim.setValue("a", matrix)
            sim.apply(op, [0, 1])"""

        # test inverse basica gate
        op = InverseBasicGate("b", 1)
        # matrix = np.array([[1, 0], [0, 1]])
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "Parameter " + str(op.name) + " in InverseBasicGate is undefined."
        )

        """with pytest.raises(
            ValueError,
            match=re.escape(f"Gate {op} not found"),
        ):
            sim.apply(op, [0])"""

        """with pytest.raises(
            ValueError,
            match=re.escape("Wrong number of targets"),
        ):
            sim.setValue("b", matrix)
            sim.apply(op, [0, 1])"""

        # test phase/ inverse phase
        '''gates = [
            Phase("c"),
            InversePhase("c"),
            Rx("c"),
            Ry("c"),
            Rz("c"),
            Rzz("c"),
            InverseRx("c"),
            InverseRy("c"),
            InverseRz("c"),
            InverseRzz("c"),
        ]
        for op in gates:
            with pytest.raises(Exception) as exc_info:
                targets = [0] if op.getNumberQubits() == 1 else [0, 1]
                sim.apply(op, targets)
            exc = exc_info.value
            assert exc.args[0] == "phase " + str(op.name) + " not defined"'''

        # sim = simulatorStatevectorNumpy(3, 3)
        # op = QuantumControl([1], Hadamard())
        # sim.apply(op, [0, 1], extraControls=[0])
