import geqo.algorithms as algorithms
import geqo.gates as gates
import geqo.initialization as initialization
import geqo.operations as operations
import geqo.simulators as simulators
import geqo.utils as utils
from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation

from .__deps__ import _OPTIONAL_VISUALIZATION_ENABLED


# Lazy import of optional deps
def __getattr__(attr):
    if attr == "visualization":
        if _OPTIONAL_VISUALIZATION_ENABLED:
            import geqo.visualization as visualization

            return visualization
        else:
            raise AttributeError(
                """
                geqo.visualization optional feature is not enabled.
                Please install with pip install geqo[visualization] to use this function.
                """
            )


__version__ = "0.1.0"
__all__ = [
    "algorithms",
    "gates",
    "operations",
    "initialization",
    "simulators",
    "utils",
    "BasicGate",
    "InverseBasicGate",
    "QuantumOperation",
    "Sequence",
]
