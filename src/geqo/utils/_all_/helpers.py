import sympy as sym
import numpy as np
from numpy.typing import NDArray

from geqo.utils._numpy_.helpers import (
    getSingleQubitOperationOnRegister as getSingleQubitOperationOnRegisterNumpy,
    partialTrace as partialTraceNumpy,
)
from geqo.utils._sympy_.helpers import (
    getSingleQubitOperationOnRegister as getSingleQubitOperationOnRegisterSympy,
    partialTrace as partialTraceSympy,
)


def getSingleQubitOperationOnRegister(
    u: sym.Matrix | NDArray, numberQubits: int, targets: list[int]
) -> sym.Matrix | NDArray:
    """Apply single-qubit operation to specific qubits in register."""
    if isinstance(u, np.ndarray):
        return getSingleQubitOperationOnRegisterNumpy(u, numberQubits, targets)
    return getSingleQubitOperationOnRegisterSympy(u, numberQubits, targets)


def partialTrace(
    rho: sym.Matrix | NDArray, qubits: list[int], dropTargets: list[int]
) -> tuple[sym.Matrix, sym.Matrix] | tuple[NDArray, NDArray]:
    """Compute partial trace of density matrix."""
    if isinstance(rho, np.ndarray):
        return partialTraceNumpy(rho, qubits, dropTargets)
    return partialTraceSympy(rho, qubits, dropTargets)
