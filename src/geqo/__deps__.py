_OPTIONAL_VISUALIZATION_ENABLED = False

_OPTIONAL_SYMPY_SIMULATORS_ENABLED = False
_OPTIONAL_NUMPY_SIMULATORS_ENABLED = False


def _check_opt_deps():
    global _OPTIONAL_VISUALIZATION_ENABLED
    global _OPTIONAL_SYMPY_SIMULATORS_ENABLED
    global _OPTIONAL_NUMPY_SIMULATORS_ENABLED

    try:
        import IPython  # noqa: F401
        import matplotlib  # noqa: F401

        _OPTIONAL_VISUALIZATION_ENABLED = True
    except ImportError:
        _OPTIONAL_VISUALIZATION_ENABLED = False
    try:
        import sympy  # noqa: F401

        _OPTIONAL_SYMPY_SIMULATORS_ENABLED = True
    except ImportError:
        _OPTIONAL_SYMPY_SIMULATORS_ENABLED = False
    try:
        import numpy  # noqa: F401

        _OPTIONAL_NUMPY_SIMULATORS_ENABLED = True
    except ImportError:
        _OPTIONAL_NUMPY_SIMULATORS_ENABLED = False


_check_opt_deps()
