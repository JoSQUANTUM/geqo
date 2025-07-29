from ..__deps__ import (
    _OPTIONAL_NUMPY_SIMULATORS_ENABLED,
    _OPTIONAL_SYMPY_SIMULATORS_ENABLED,
)

from geqo.utils._base_.helpers import (
    bin2num,
    num2bin,
    embedSequences,
    getSingleQubitOperationOnRegister,
    partialTrace,
    partial_diag,
)

if (not _OPTIONAL_SYMPY_SIMULATORS_ENABLED) and (
    not _OPTIONAL_NUMPY_SIMULATORS_ENABLED
):
    from geqo.utils._base_.helpers import (
        getSingleQubitOperationOnRegister,
        partialTrace,
    )

elif (_OPTIONAL_SYMPY_SIMULATORS_ENABLED) and (not _OPTIONAL_NUMPY_SIMULATORS_ENABLED):
    from geqo.utils._sympy_.helpers import (
        getSingleQubitOperationOnRegister,
        partialTrace,
        projection,
        permutationMatrixQubitsSymPy,
        multiQubitsUnitary,
        newPartialTrace,
    )

elif (not _OPTIONAL_SYMPY_SIMULATORS_ENABLED) and (_OPTIONAL_NUMPY_SIMULATORS_ENABLED):
    from geqo.utils._numpy_.helpers import (
        getSingleQubitOperationOnRegister,
        partialTrace,
        permutationMatrixQubitsNumPy,
    )

else:
    from geqo.utils._all_.helpers import (
        getSingleQubitOperationOnRegister,
        partialTrace,
    )

    from geqo.utils._sympy_.helpers import (
        permutationMatrixQubitsSymPy,
    )

    from geqo.utils._numpy_.helpers import (
        permutationMatrixQubitsNumPy,
    )

__all__ = [
    "bin2num",
    "num2bin",
    "embedSequences",
    "getSingleQubitOperationOnRegister",
    "partialTrace",
    "permutationMatrixQubitsNumPy",
    "permutationMatrixQubitsSymPy",
    "partial_diag",
    "projection",
    "multiQubitsUnitary",
    "newPartialTrace",
]
