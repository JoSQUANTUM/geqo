from geqo.core.basic import BasicGate, InverseBasicGate

from geqo.gates.fundamental_gates import (
    PauliX,
    PauliY,
    PauliZ,
    SwapQubits,
    Hadamard,
    Phase,
    InversePhase,
    CNOT,
    SGate,
    InverseSGate,
)
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
from geqo.gates.multi_qubit_gates import Toffoli
from geqo.algorithms.algorithms import (
    PermuteQubits,
    QubitReversal,
    PCCM,
    QFT,
    InversePCCM,
    InverseQFT,
)
from geqo.core.quantum_circuit import Sequence
from geqo.initialization.state import SetBits, SetQubits, SetDensityMatrix
from geqo.operations.measurement import Measure, DropQubits
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.core.quantum_operation import QuantumOperation

from geqo.simulators.sympy.implementation import (
    ensembleSimulatorSymPy,
    mixedStateSimulatorSymPy,
    simulatorUnitarySymPy,
    newSimulatorUnitarySymPy,
    getUnitarySymPy,
)

import pytest
from sympy import Symbol, S, Rational
import sympy as sym
import numpy as np


gates = [
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


class TestSympySimulators:
    def test_get_unitary(self):
        sim = ensembleSimulatorSymPy(0, 2)
        op1 = BasicGate("a", 1)
        op2 = InverseBasicGate("a", 1)
        matrix = sym.Matrix([[1, 0], [0, 1]])

        with pytest.raises(Exception) as exc_info:
            getUnitarySymPy(op1, sim.values)
        exc = exc_info.value
        assert (
            exc.args[0] == "Parameter " + str(op1.name) + " in BasicGate is undefined."
        )

        with pytest.raises(Exception) as exc_info:
            getUnitarySymPy(op2, sim.values)
        exc = exc_info.value
        assert (
            exc.args[0]
            == "Parameter " + str(op2.name) + " in InverseBasicGate is undefined."
        )

        sim.setValue("a", matrix)
        u1 = getUnitarySymPy(op1, sim.values)
        u2 = getUnitarySymPy(op2, sim.values)

        assert u1 == matrix
        assert u2 == matrix

        op1 = Rzz("b")
        op2 = InverseRzz("b")
        sim.setValue("b", 1.23)
        u1 = getUnitarySymPy(op1, sim.values)
        u2 = getUnitarySymPy(op2, sim.values)
        assert u1 * u2 == sym.eye(4)

        with pytest.raises(Exception) as exc_info:
            getUnitarySymPy(QFT(2), sim.values)
        exc = exc_info.value
        assert exc.args[0] == "gate " + str(QFT(2)) + " not implemented yet"

    def test_ensemble_simulator(self):
        nqubits = 3
        ncbits = 2
        sim = ensembleSimulatorSymPy(ncbits, nqubits)
        rho = sym.zeros(2**nqubits, 2**nqubits)
        rho[0, 0] = 1

        assert sim.numberBits == ncbits
        assert sim.numberQubits == nqubits
        assert sim.ensemble == {(0,) * ncbits: (1, rho)}
        assert sim.values == {}
        assert (
            str(sim)
            == "ensembleSimulatorSymPy(" + str(ncbits) + ", " + str(nqubits) + ")"
        )

        sim.setValue("a", 1.23)
        b = Symbol("b")
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "Ph1": S.Pi / 2,
            "RX(π/2)": S.Pi / 2,
            "RX(-π/2)": -S.Pi / 2,
            "RY(-π/2)": -S.Pi / 2,
            "RX(a)": 1.23,
            "RX(b)": b,
            "S.Pi/4": S.Pi / 4,
            "-S.Pi/4": -S.Pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

    def test_ensemble_simulator_classical_control(self):
        nqubits = 2
        ncbits = 2
        sim = ensembleSimulatorSymPy(ncbits, nqubits)
        sim.prepareBackend([QFT(2)])
        seq = Sequence(
            [0, 1],
            [0, 1],
            [
                (Hadamard(), [0]),
                (Measure(2), [0, 1], [0, 1]),
                (ClassicalControl([1, 0], QFT(2)), [0, 1, 0, 1]),
            ],
        )
        sim.apply(seq, [0, 1], [0, 1])

        assert sim.ensemble == {
            (0, 0): (
                Rational(1, 2),
                sym.Matrix(
                    [
                        [1, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                    ]
                ),
            ),
            (1, 0): (
                Rational(1, 2),
                sym.Matrix(
                    [
                        [
                            Rational(1, 4),
                            Rational(-1, 4),
                            Rational(1, 4),
                            Rational(-1, 4),
                        ],
                        [
                            Rational(-1, 4),
                            Rational(1, 4),
                            Rational(-1, 4),
                            Rational(1, 4),
                        ],
                        [
                            Rational(1, 4),
                            Rational(-1, 4),
                            Rational(1, 4),
                            Rational(-1, 4),
                        ],
                        [
                            Rational(-1, 4),
                            Rational(1, 4),
                            Rational(-1, 4),
                            Rational(1, 4),
                        ],
                    ]
                ),
            ),
        }
        with pytest.raises(Exception) as exc_info:
            sim.apply(ClassicalControl([0, 0], Measure(2)), [0, 1], [0, 1])
        exc = exc_info.value
        assert exc.args[0] == "Controlled operations cannot be non-unitary."

        with pytest.raises(Exception) as exc_info:
            sim.apply(
                ClassicalControl([0, 0], Sequence([0], [0], [(Measure(1), [0], [0])])),
                [0, 1],
                [0, 1],
            )
        exc = exc_info.value
        assert exc.args[0] == "Controlled operations cannot be non-unitary."

    def test_ensemble_simulator_unitary(self):
        sim = ensembleSimulatorSymPy(2, 2)
        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1], [0, 1])
        rho = sim.ensemble[(0, 0)][1]
        rho = rho.applyfunc(sym.re)
        rho = np.array(rho.evalf(), dtype=np.float64)
        expect = np.zeros((4, 4), dtype=np.float64)
        expect[0, 0] = 1
        np.testing.assert_allclose(expect, rho, rtol=1e-7, atol=1e-9)

    def test_ensemble_simulator_non_unitary(self):
        # test setdensitymatix
        sim = ensembleSimulatorSymPy(2, 2)
        op = SetDensityMatrix("d1", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        rho = sym.Matrix(
            [[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        )
        sim.setValue("d1", rho)
        sim.apply(op, [0, 1], [0, 1])
        assert sim.ensemble[(0, 0)][1] == rho

        # test measuring partial qubits
        sim.apply(Measure(1), [0], [0])
        assert float(sim.ensemble[(0, 0)][0]) == 1.0

        # test multiple rounds of measurement
        sim.apply(Measure(2), [0, 1], [0, 1])
        sim.apply(Hadamard(), [1])
        sim.apply(Measure(2), [0, 1], [0, 1])

        # test setbits
        sim.apply(Hadamard(), [0])
        sim.apply(Measure(2), [0, 1], [0, 1])
        op = SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        sim.setValue("sb", [1])
        sim.apply(op, [0])
        for key in list(sim.ensemble.keys()):
            assert key[0] == 1

        # test setqubits
        op = SetQubits("sq", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        sim.setValue("sq", [1, 0])
        sim.apply(op, [0, 1])
        rho = np.zeros((4, 4))
        rho[2, 2] = 1
        for key, item in sim.ensemble.items():
            s = np.array(item[1].evalf(), dtype=np.float64)
            np.testing.assert_allclose(s, rho, rtol=1e-7, atol=1e-9)

        # test dropqubits
        sim.apply(DropQubits(1), [0])
        assert sim.numberQubits == 1
        assert sim.ensemble[(1, 1)][1].shape == (2, 2)

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
        assert exc.args[0] == f"gate not implemented for ensembleSimulatorSymPy: {op}"
        # assert exc.args[1] == op

    def test_mixedstate_simulator(self):
        nqubits = 3
        ncbits = 2
        sim = mixedStateSimulatorSymPy(ncbits, nqubits, return_density=True)
        rho = sym.zeros(2**nqubits, 2**nqubits)
        rho[0, 0] = 1

        assert sim.numberBits == ncbits
        assert sim.numberQubits == nqubits
        assert sim.densityMatrix == rho
        assert sim.return_density
        assert sim.values == {}
        assert (
            str(sim)
            == "mixedStateSimulatorSymPy(" + str(ncbits) + ", " + str(nqubits) + ")"
        )

        sim.setValue("a", 1.23)
        b = Symbol("b")
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "Ph1": S.Pi / 2,
            "RX(π/2)": S.Pi / 2,
            "RX(-π/2)": -S.Pi / 2,
            "RY(-π/2)": -S.Pi / 2,
            "RX(a)": 1.23,
            "RX(b)": b,
            "S.Pi/4": S.Pi / 4,
            "-S.Pi/4": -S.Pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "prepareBackend: operation not supported:"
        assert str(Hadamard()) in exc.args[1]

    def test_mixedstate_simulator_unitary(self):
        sim = mixedStateSimulatorSymPy(2, 2)
        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1], [0, 1])
        rho = sim.densityMatrix
        rho = rho.applyfunc(sym.re)
        rho = np.array(rho.evalf(), dtype=np.float64)
        expect = np.zeros((4, 4), dtype=np.float64)
        expect[0, 0] = 1
        np.testing.assert_allclose(expect, rho, rtol=1e-7, atol=1e-9)

    def test_mixedstate_simulator_non_unitary(self):
        # test setdensitymatix
        sim = mixedStateSimulatorSymPy(2, 2, return_density=True)
        op = SetDensityMatrix("d1", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        rho = sym.Matrix(
            [[0.5, 0.5, 0, 0], [0.5, 0.5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        )
        sim.setValue("d1", rho)
        sim.apply(op, [0, 1], [0, 1])
        assert sim.densityMatrix == rho

        # test measuring partial qubits
        sim.apply(Measure(1), [0], [0])
        assert float(sim.measureHistory[0][(0,)]) == 1.0

        # test multiple rounds of measurement
        sim.apply(Measure(2), [0, 1], [0, 1])
        sim.apply(Hadamard(), [1])
        sim.apply(Measure(2), [0, 1], [0, 1])

        rho = np.zeros((4, 4))
        rho[0, 0] = 0.5
        rho[1, 1] = 0.5
        s = np.array(sim.densityMatrix.evalf(), dtype=np.float64)
        np.testing.assert_allclose(s, rho, rtol=1e-7, atol=1e-9)
        s2 = np.array(sim.measureHistory[-1]["mixed_state"].evalf(), dtype=np.float64)
        np.testing.assert_allclose(s2, rho, rtol=1e-7, atol=1e-9)

        # test setbits
        sim.apply(Hadamard(), [0])
        sim.apply(Measure(2), [0, 1], [0, 1])
        op = SetBits("sb", 1)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0])
        exc = exc_info.value
        assert exc.args[0] == "SetBits not supported by this simulator"

        # test setqubits
        op = SetQubits("sq", 2)
        with pytest.raises(Exception) as exc_info:
            sim.apply(op, [0, 1], [0, 1])
        exc = exc_info.value
        assert (
            exc.args[0]
            == "name of parameter " + str(op.name) + " not known to simulator"
        )

        sim.setValue("sq", [1, 0])
        sim.apply(op, [0, 1])
        rho = np.zeros((4, 4))
        rho[2, 2] = 1
        s = np.array(sim.densityMatrix.evalf(), dtype=np.float64)
        np.testing.assert_allclose(s, rho, rtol=1e-7, atol=1e-9)

        # test dropqubits
        sim.apply(DropQubits(1), [0])
        assert sim.numberQubits == 1
        assert sim.densityMatrix.shape == (2, 2)

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
        assert exc.args[0] == f"gate not implemented for mixedStateSimulatorSymPy: {op}"
        # assert exc.args[1] == op

    def test_unitary_simulator(self):
        nqubits = 2
        sim = simulatorUnitarySymPy(nqubits)
        u = sym.eye(2**nqubits)

        assert sim.numberQubits == nqubits
        assert sim.u == u
        assert sim.values == {}
        assert str(sim) == "simulatorUnitarySymPy(" + str(nqubits) + ")"

        sim.setValue("a", 1.23)
        b = Symbol("b")
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "Ph1": S.Pi / 2,
            "RX(π/2)": S.Pi / 2,
            "RX(-π/2)": -S.Pi / 2,
            "RY(-π/2)": -S.Pi / 2,
            "RX(a)": 1.23,
            "RX(b)": b,
            "S.Pi/4": S.Pi / 4,
            "-S.Pi/4": -S.Pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "operation not supported:"
        assert str(Hadamard()) in exc.args[1]

        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1])
        expect = np.eye(4, dtype=np.float64)
        s = np.array(sim.u, dtype=np.float64)
        np.testing.assert_allclose(expect, s, rtol=1e-7, atol=1e-9)

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
            sim.apply(op, [0, 1])
        exc = exc_info.value
        assert exc.args[0] == f"gate not implemented for simulatorUnitarySymPy: {op}"
        # assert exc.args[1] == op

    def test_new_unitary_simulator(self):
        nqubits = 2
        sim = newSimulatorUnitarySymPy(nqubits)
        u = sym.eye(2**nqubits)

        assert sim.numberQubits == nqubits
        assert sim.u == u
        assert sim.values == {}
        assert str(sim) == "newSimulatorUnitarySymPy(" + str(nqubits) + ")"

        sim.setValue("a", 1.23)
        b = Symbol("b")
        sim.prepareBackend(
            [QFT(2), InverseQFT(2), PCCM("a"), InversePCCM("b"), Toffoli()]
        )
        assert sim.values == {
            "a": 1.23,
            "Ph1": S.Pi / 2,
            "RX(π/2)": S.Pi / 2,
            "RX(-π/2)": -S.Pi / 2,
            "RY(-π/2)": -S.Pi / 2,
            "RX(a)": 1.23,
            "RX(b)": b,
            "S.Pi/4": S.Pi / 4,
            "-S.Pi/4": -S.Pi / 4,
        }

        with pytest.raises(Exception) as exc_info:
            sim.prepareBackend([Hadamard()])
        exc = exc_info.value
        assert exc.args[0] == "operation not supported:"
        assert str(Hadamard()) in exc.args[1]

        sim.setValue("a", 0.1)
        sim.apply(identity_seq, [0, 1])
        expect = np.eye(4, dtype=np.float64)
        s = np.array(sim.u, dtype=np.float64)
        np.testing.assert_allclose(expect, s, rtol=1e-7, atol=1e-9)

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
            sim.apply(op, [0, 1])
        exc = exc_info.value
        assert exc.args[0] == f"gate not implemented for newSimulatorUnitarySymPy: {op}"
        # assert exc.args[1] == op
