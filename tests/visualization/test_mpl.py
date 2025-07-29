from geqo.visualization.mpl import plot_mpl, plot_hist

from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
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
from geqo.gates.multi_qubit_gates import Toffoli
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
from geqo.algorithms.algorithms import (
    PCCM,
    QFT,
    InversePCCM,
    InverseQFT,
    PermuteQubits,
    QubitReversal,
)
from geqo.initialization.state import SetBits, SetQubits, SetDensityMatrix
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.operations.measurement import Measure, DropQubits
from geqo.simulators.sympy.implementation import (
    ensembleSimulatorSymPy,
    mixedStateSimulatorSymPy,
)
from geqo.simulators.numpy.implementation import simulatorStatevectorNumpy

import matplotlib.pyplot as plt
from sympy import Symbol
import numpy as np
import pytest
import random
import os

nongate = [1, 2, 3]
jos = BasicGate("JoS", 2)
wow = InverseBasicGate("WoW", 3)
geqo = BasicGate("geqo", 3)
cjos = QuantumControl([1, 0], jos)
cccx = QuantumControl([0, 1, 0], PauliX())
ch = QuantumControl([0], Hadamard())
cry = QuantumControl([1], InverseRy("alpha"))
crzz = QuantumControl([0, 1, 0], Rzz("nu"))
cwow = QuantumControl([1, 0], wow)
cgeqo = QuantumControl([1, 0, 1], geqo)
ccjos = QuantumControl([0, 1], cjos)
ccnot = QuantumControl([1], CNOT())
ctoffoli = QuantumControl([0], Toffoli())
measure = Measure(4)
perm = PermuteQubits([2, 1, 0])
drop = DropQubits(2)
s1 = SetBits("set1", 3)
s2 = SetBits("set2", 2)
s3 = SetBits("set3", 1)
sq = SetQubits("sq", 3)
sq2 = SetQubits("sq2", 1)
sden = SetDensityMatrix("d", 3)
sden2 = SetDensityMatrix("d2", 1)
cr = QuantumControl([0, 1], QubitReversal(3))
cswap = QuantumControl([1, 0], SwapQubits())
cpcm = QuantumControl([0, 1], InversePCCM("sigma"))
cp = QuantumControl([0, 1], Phase("delta"))
cqft = QuantumControl([1, 1, 0], QFT(3))
cperm = QuantumControl([1], PermuteQubits([1, 0, 2]))
cs = QuantumControl([0], SGate())
classical_jos = ClassicalControl([1, 0, 1], jos)
classical_h = ClassicalControl([1], Hadamard())
classical_not = ClassicalControl([0, 1], PauliX())
classical_cnot = ClassicalControl([1], CNOT())
classical_toffoli = ClassicalControl([0], Toffoli())
classical_swap = ClassicalControl([0], SwapQubits())
classical_qctrl = ClassicalControl([1, 0], cqft)
subseq = Sequence(
    [0, 1, 2],
    [0, 1, 2],
    [(Hadamard(), [2]), (CNOT(), [1, 0]), (SwapQubits(), [0, 2])],
    name="sbsq",
)


operations = [
    (nongate, [1]),
    (nongate, [0, 1, 2]),
    (PauliZ(), [4]),
    (PauliY(), [3]),
    (PauliX(), [2]),
    (ch, [3, 0]),
    (SGate(), [4]),
    (InverseSGate(), [5]),
    (Phase("alpha"), [1]),
    (InversePhase("beta"), [0]),
    (cp, [1, 4, 5]),
    (cs, [1, 1]),
    (Rx("gamma"), [0]),
    (Ry("lambda"), [1]),
    (Rz("kappa"), [2]),
    (cry, [4, 1]),
    (InverseRx("x"), [5]),
    (InverseRz("z"), [0]),
    (InverseRzz("g"), [5, 3]),
    (crzz, [0, 3, 5, 1, 4]),
    (CNOT(), [3, 0]),
    (Toffoli(), [0, 4, 2]),
    (Toffoli(), [1, 3, 5]),
    (Toffoli(), [4, 5, 1]),
    (cccx, [0, 1, 4, 3]),
    (SwapQubits(), [2, 5]),
    (QubitReversal(5), [2, 3, 0, 4, 1]),
    (cswap, [0, 3, 2, 5]),
    (cr, [5, 2, 0, 4, 1]),
    (perm, [1, 3, 5]),
    (QFT(3), [2, 3, 0]),
    (InverseQFT(2), [4, 5]),
    (cqft, [0, 1, 5, 4, 2, 3]),
    (jos, [0, 1]),
    (cjos, [4, 0, 3, 2]),
    (cjos, [0, 2, 1, 3]),
    (cwow, [4, 2, 3, 0, 1]),
    (cwow, [0, 3, 1, 2, 5]),
    (cgeqo, [5, 0, 2, 4, 3, 1]),
    (PCCM("psi"), [4, 1]),
    (InversePCCM("omega"), [1, 2]),
    (cpcm, [0, 3, 2, 5]),
    (cperm, [2, 3, 4, 5]),
    (drop, [2, 4]),
    (s1, [1, 3, 4]),
    (s2, [0, 5]),
    (s3, [2]),
    (sq, [1, 4, 5]),
    (sq2, [3]),
    (sden, [0, 3, 2]),
    (sden2, [5]),
    (subseq, [4, 2, 3]),
    (classical_jos, [0, 3, 5, 1, 4]),
    (classical_h, [2, 2]),
    (measure, [0, 2, 3, 5], [0, 2, 3, 5]),
    (ccjos, [0, 1, 2, 3, 4, 5]),
    (ccnot, [2, 4, 1]),
    (ccnot, [1, 4, 1]),
    (ctoffoli, [5, 0, 3, 2]),
    (classical_not, [0, 1, 4]),
    (classical_not, [0, 3, 2]),
    (classical_cnot, [3, 5, 2]),
    (classical_toffoli, [2, 1, 0, 5]),
    (classical_swap, [1, 2, 3]),
    (classical_qctrl, [2, 4, 0, 1, 2, 3, 4, 5]),
    (classical_qctrl, [2, 3, 0, 3, 2, 1, 4, 5]),
    (Measure(1), [3], [4]),
    (DropQubits(1), [0]),
]

qubits = [f"q_{i}" for i in range(6)]
seq = Sequence([0, 1, 2, 3, 4, 5], qubits, operations)
# sim = ensembleSimulatorSymPy(6, 6)
# sim.setValue("alpha", 0.1234)
# sim.setValue("omega", 1.5677)
# sim.setValue("set2", [0, 1])
# sim.setValue("sq", [1, 0, 1])


class TestVisualization:
    def test_plot_mpl_backend_greek(self):
        import matplotlib

        matplotlib.use("Agg")  # avoid showing the figure
        sim = ensembleSimulatorSymPy(6, 6)
        sim.setValue("alpha", Symbol("a"))
        sim.setValue("omega", 1.5677)
        sim.setValue("sigma", 0.66)
        sim.setValue("set2", [0, 1])
        sim.setValue("set3", [1])
        sim.setValue(
            "sq", [1, 0, 1]
        )  # set values for SetQubits (compared to not specifing values)
        plot_mpl(
            seq,
            backend=sim,
            decompose_subseq=True,
            pack=True,
            fold=18,
            style="geqo",
            greek_symbol=True,
            filename=None,
        )
        plt.close()

    def test_plot_mpl_no_backend_greek(self):
        import matplotlib

        matplotlib.use("Agg")

        plot_mpl(
            seq,
            backend=None,
            decompose_subseq=True,
            pack=False,
            fold=18,
            style="geqo",
            greek_symbol=True,
            filename=None,
        )
        plt.close()

    def test_plot_mpl_backend_no_greek(self):
        import matplotlib

        matplotlib.use("Agg")
        sim = ensembleSimulatorSymPy(6, 6)
        sim.setValue("alpha", 0.1234)
        sim.setValue("omega", 1.5677)
        sim.setValue("set2", [0, 1])
        plot_mpl(
            seq,
            backend=sim,
            decompose_subseq=False,
            pack=True,
            fold=18,
            style="geqo",
            greek_symbol=False,
            filename=None,
        )
        plt.close()

    def test_plot_mpl_no_backend_no_greek(self):
        import matplotlib

        matplotlib.use("Agg")

        plot_mpl(
            seq,
            backend=None,
            decompose_subseq=True,
            pack=True,
            fold=18,
            style="geqo",
            greek_symbol=False,
            filename=None,
        )
        plt.close()

    def test_quantum_control_non_unitary(self):
        import matplotlib

        matplotlib.use("Agg")
        non_unitaries = [
            Measure(2),
            DropQubits(2),
            SetBits("s", 2),
            SetQubits("s", 2),
            SetDensityMatrix("d", 2),
        ]
        non_unitary = random.choice(non_unitaries)
        op = QuantumControl([0], non_unitary)
        with pytest.raises(
            TypeError,
            match="Non-unitary operations are not eligible targets for QuantumControl",
        ):
            seq = Sequence([0, 1, 2], [0, 1, 2], [(op, [0, 1, 2])])
            plot_mpl(seq)
            plt.close()

    def test_plot_mpl_saves_file(self):
        import matplotlib

        matplotlib.use("Agg")
        test_file = "test_plot_output"
        try:
            plot_mpl(seq, filename=test_file)
            plt.close()
            assert os.path.exists(f"{test_file}.png")
        finally:
            if os.path.exists(f"{test_file}.png"):
                os.remove(f"{test_file}.png")

    def test_plot_hist_saves_file_small(self):
        import matplotlib

        matplotlib.use("Agg")

        test_file = "test_plot_output"

        try:
            dic = {(0, 0): 0.5, (0, 1): 0.5}
            plot_hist(dic, filename=test_file)
            plt.close()
            assert os.path.exists(f"{test_file}.png")
        finally:
            if os.path.exists(f"{test_file}.png"):
                os.remove(f"{test_file}.png")

    def test_plot_hist_saves_file_large(self):
        import matplotlib

        matplotlib.use("Agg")

        test_file = "test_plot_output"

        try:
            bstrs = [bin(i)[2:].zfill(7) for i in range(2**7)]
            tuples = [tuple([int(b) for b in bstr]) for bstr in bstrs]
            dicc = {t: 1 / 2**7 for t in tuples}
            plot_hist(dicc, filename=test_file)
            plt.close()
            assert os.path.exists(f"{test_file}.png")
        finally:
            if os.path.exists(f"{test_file}.png"):
                os.remove(f"{test_file}.png")

    def test_non_ensemble_plot_hist(self):
        import matplotlib

        matplotlib.use("Agg")
        for n in range(5, 8):
            names = [f"a_{i}" for i in range(n)]
            op = [(Ry(names[i]), [i]) for i in range(n)]
            op.append((Measure(n), [*range(n)], [*range(n)]))
            seq = Sequence([*range(n)], [*range(n)], op)
            sim1 = mixedStateSimulatorSymPy(n, n)
            sim2 = simulatorStatevectorNumpy(n, n)
            values = np.random.uniform(0, 2 * np.pi, n)
            for idx, name in enumerate(names):
                sim1.setValue(name, values[idx])
                sim2.setValue(name, values[idx])
            sim1.apply(seq, [*range(n)], [*range(n)])
            sim2.apply(seq, [*range(n)], [*range(n)])

            plot_hist(sim1.measureHistory[0], show_bar_labels=False)
            plt.close()
            plot_hist(sim1.measureHistory[0], show_bar_labels=True)
            plt.close()
            plot_hist(sim2.measurementResult, show_bar_labels=False)
            plt.close()
            plot_hist(sim2.measurementResult, show_bar_labels=True)
            plt.close()

    def test_ensemble_plot_hist(self):
        import matplotlib

        matplotlib.use("Agg")
        names = [f"a_{i}" for i in range(3)]
        op = [(Ry(names[i]), [i]) for i in range(3)]
        op.append((Measure(3), [*range(3)], [*range(3)]))
        seq = Sequence([*range(3)], [*range(3)], op)
        sim = ensembleSimulatorSymPy(3, 3)
        values = np.random.uniform(0, 2 * np.pi, 3)
        for idx, name in enumerate(names):
            sim.setValue(name, values[idx])
        sim.apply(seq, [*range(3)], [*range(3)])

        plot_hist(sim.ensemble, show_bar_labels=True)
        plt.close()
        plot_hist(sim.ensemble, show_bar_labels=False)
        plt.close()

    def test_plot_hist_equal_prob(self):
        import matplotlib

        matplotlib.use("Agg")
        bstrs = [bin(i)[2:].zfill(7) for i in range(2**7)]
        tuples = [tuple([int(b) for b in bstr]) for bstr in bstrs]
        dicc = {t: 1 / 2**7 for t in tuples}
        plot_hist(dicc)
        plt.close()
