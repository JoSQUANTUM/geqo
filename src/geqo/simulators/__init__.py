from ..__deps__ import (
    _OPTIONAL_NUMPY_SIMULATORS_ENABLED,
    _OPTIONAL_SYMPY_SIMULATORS_ENABLED,
)

from geqo.simulators.base import Simulator  # noqa: F401

__base_simulators__ = [
    "Simulator",
    "Sequence2QASM",
]

__numpy_simulators__ = [
    "simulatorStatevectorNumpy",
]
__sympy_simulators__ = [
    "ensembleSimulatorSymPy",
    "simulatorUnitarySymPy",
    "ensembleSimulatorSymPy",
    "mixedStateSimulatorSymPy",
    "newSimulatorUnitarySymPy",
]

__simulators__ = __base_simulators__
if _OPTIONAL_SYMPY_SIMULATORS_ENABLED:
    from geqo.simulators.sympy import (
        mixedStateSimulatorSymPy,  # noqa: F401
        simulatorUnitarySymPy,  # noqa: F401
        newSimulatorUnitarySymPy,  # noqa: F401
        ensembleSimulatorSymPy,  # noqa: F401
    )  # noqa: F401

    __simulators__ += __sympy_simulators__
if _OPTIONAL_NUMPY_SIMULATORS_ENABLED:
    from geqo.simulators.numpy import simulatorStatevectorNumpy  # noqa: F401

    __simulators__ += __numpy_simulators__


def __getattr__(attr: str):
    attr = attr.lower()
    if not _OPTIONAL_SYMPY_SIMULATORS_ENABLED and "sympy" in attr:
        raise AttributeError(
            """
            geqo.simulators.sympy optional feature is not enabled.
            Please install with pip install geqo[sympy] to use this function.
            """
        )
    if not _OPTIONAL_NUMPY_SIMULATORS_ENABLED and "numpy" in attr:
        raise AttributeError(
            """
            geqo.simulators.numpy optional feature is not enabled.
            Please install with pip install geqo[numpy] to use this function.
            """
        )


__all__ = __simulators__
