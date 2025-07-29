from geqo.utils._sympy_.helpers import newPartialTrace
from geqo.utils._base_.helpers import embedSequences
from geqo.utils._all_.helpers import partialTrace
from geqo.core.quantum_circuit import Sequence
from geqo.gates.fundamental_gates import Hadamard, CNOT
from geqo.operations.measurement import Measure
import sympy as sym
import numpy as np


class TestHelpers:
    def test_embed_sequence_with_measure(self):
        subseq = Sequence(
            [0, 1],
            ["q0", "q1"],
            [
                (CNOT(), ["q1", "q0"]),
                (Hadamard(), ["q0"]),
                (Measure(2), ["q0", "q1"], [0, 1]),
            ],
        )
        seq = Sequence(
            [0, 1, 2],
            [0, 1, 2],
            [(Hadamard(), [2]), (subseq, [2, 0]), (CNOT(), [1, 2])],
        )
        seq = embedSequences(seq)
        assert seq == Sequence(
            [0, 1, 2],
            [0, 1, 2],
            [
                (Hadamard(), [2]),
                (CNOT(), [0, 2]),
                (Hadamard(), [2]),
                (Measure(2), [2, 0], [2, 0]),
                (CNOT(), [1, 2]),
            ],
        )

    def test_newPartialTrace(self):
        amp = [0.7**0.5, 0.2**0.5, 0.1**0.5]
        state = np.zeros(16)
        for idx, item in enumerate([2, 7, 14]):
            state[item] = amp[idx]
        rho = np.outer(state, state)
        rho = sym.Matrix(rho)

        part_rho, _ = partialTrace(rho, [0, 1, 2, 3], [1, 3])
        part_rho_new = newPartialTrace(rho, [0, 1, 2, 3], [1, 3])

        s1 = np.array(part_rho.evalf(), dtype=np.float64)
        s2 = np.array(part_rho_new.evalf(), dtype=np.float64)
        np.testing.assert_allclose(s1, s2, rtol=1e-7, atol=1e-9)
