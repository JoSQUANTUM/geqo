from sympy import Symbol

import geqo.algorithms as Algorithms
import geqo.gates as Gates
from geqo.__logger__ import get_logger
from geqo.algorithms.algorithms import PermuteQubits
from geqo.core.quantum_operation import QuantumOperation
from geqo.operations.measurement import Measure
from geqo.simulators.base import Simulator

logger = get_logger(__name__)

# fmt: off
# valid greek letters
greek_letters = {
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
    "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega", "Gamma", "Delta",
    "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi", "Psi", "Omega"
}
# fmt: on


def valid_name(name: str):
    """Check if the gate/sequence name is valid for visualization (e.g., not too long).

    Args:
        name (str): The user-defined gate name.

    Raises:
        TypeError: If the name is not a string.
        ValueError: If the name is too long or violates capitalization rules.

    Returns:
        None: If the name is valid.

    """
    if not isinstance(name, str):
        logger.warning("invalid gate/sequence name: %s", name)
        raise TypeError("Gate/Sequence name must be a string.")
    if name != r"\mathbb{R}\text{vrs}" and r"\rho" not in name:
        if len(name) > 4:
            logger.warning("invalid gate/sequence name: %s", name)
            raise ValueError(
                "Gate/Sequence names with 2 or more capital letters can have at most 3 letters in total. \n Gate names with fewer than 2 capital letters can have at most 4 letters in total."
            )

        elif sum(1 for letter in name if letter.isupper()) >= 2:
            if len(name) > 3:
                logger.warning("invalid gate/sequence name: %s", name)
                raise ValueError(
                    "Gate/Sequence names with 2 or more capital letters can have at most 3 letters in total. \n Gate names with fewer than 2 capital letters can have at most 4 letters in total."
                )


def valid_angle(name: str, non_pccm: bool = True):
    """Check if the angle placeholder for a phase-related gates (e.g. Phase(), Rx(), Rzz(), PCCM()) is valid for visualization.

    Args:
        name (str): The user-defined angle placeholder.
        non_pccm (bool, optional): Set to `True` if the gate is not `PCCM()` or `InversePCCM()`. Defaults to `True`.

    Raises:
        TypeError: If the placeholder is not a string.
        ValueError: If the placeholder is too long based on the gate type.

    Returns:
        None: If the placeholder is valid.

    """
    if not isinstance(name, str):
        logger.warning("invalid gate/sequence name: %s", name)
        raise TypeError("Phase placeholder must be a string.")
    if non_pccm:
        if len(name) > 2:
            logger.info(
                "Phase placeholder '%s' is truncated to '%s'. At most 2 letters of the Phase/RotationGate placeholders can be displayed.",
                name,
                name[:2],
            )
            return name[:2]
        else:
            return name

    else:
        if len(name) > 1:
            logger.info(
                "Phase placeholder '%s' is truncated to '%s'. Only 1 letter of the (Inverse)PCCM placeholders can be displayed.",
                name,
                name[:1],
            )
            return name[:1]
        else:
            return name


def pack_gates(operations: list):
    """Compactify the circuit diagram by placing non-conflicting operations that can be implemented simultaneously into the same execution layer(column) of the circuit.

    Args:
        operations (list): A list of operations, where each operation is a tuple
            of the form (gate, target_qubits). `target_qubits` is a list of qubit indices
            the gate acts on.

    Returns:
        list: A list of columns, where each column is a list of operations
        that can be executed in parallel. The columns preserve execution order.

    """
    columns = []
    while operations:  # loop until all gates have been placed in a column
        current_col = []
        already_visited = set()  # track lines that are either already occupied by a gate or used by subsequent gate
        unplaced_gates = []  # store gates that still need to be placed

        for gate in operations:
            target = gate[1]

            if already_visited.isdisjoint(
                range(min(target), max(target) + 1)
            ):  # no conflict, place it
                current_col.append(gate)
            else:
                unplaced_gates.append(gate)  # keep for a next column
            # even if it's not placed, if the bits are used by a subsequent gate then the gate must not be placed
            if len(target) == 1:
                already_visited.update(target)
            else:
                already_visited.update(
                    range(min(target), max(target) + 1)
                )  # a multi-qubit gate "blocks" all the qubits between the min and max

        columns.append(current_col)
        operations = unplaced_gates  # update elements to only unplaced ones

    return columns


def get_gate_name(
    gate: QuantumOperation, backend: Simulator = None, greek_symbol: bool = True
):
    """Return the formatted name of a quantum gate for use in Matplotlib visualizations.

    Args:
        gate (QuantumOperation): The target quantum gate.
        backend (Simulator, optional): Backend used to resolve symbolic or numeric parameter values. Defaults to `None`.
        greek_symbol (bool, optional): Whether to convert symbolic names (e.g., parameters) into Greek letters. Defaults to `True`.

    Returns:
        str: A formatted string representing the gate's label.
        None: If the gate type is not recognized.

    """
    gate_mapping = {
        Gates.PauliX: "X",
        Gates.PauliY: "Y",
        Gates.PauliZ: "Z",
        Gates.Hadamard: "H",
        Gates.SGate: "S",
        Gates.InverseSGate: r"S$^\dagger$",
        Algorithms.QFT: "QFT",
        Algorithms.InverseQFT: r"QFT$^\dagger$",
        Algorithms.QubitReversal: r"$\mathbb{R}\text{vrs}$",
        Measure: r"$\mathbb{M}$",
        PermuteQubits: r"$\mathbb{P}\text{rmt}$",
    }

    for gate_type, name in gate_mapping.items():
        if isinstance(gate, gate_type):
            return name

    if isinstance(gate, (Gates.Phase, Gates.InversePhase)):
        inverse = False if isinstance(gate, Gates.Phase) else True
        name = phase_name_mpl(
            gate, "P", inverse, backend=backend, greek_symbol=greek_symbol
        )
        return name
    if isinstance(gate, (Gates.Rx, Gates.InverseRx)):
        inverse = False if isinstance(gate, Gates.Rx) else True
        name = phase_name_mpl(
            gate, "Rx", inverse, backend=backend, greek_symbol=greek_symbol
        )
        return name
    if isinstance(gate, (Gates.Ry, Gates.InverseRy)):
        inverse = False if isinstance(gate, Gates.Ry) else True
        name = phase_name_mpl(
            gate, "Ry", inverse, backend=backend, greek_symbol=greek_symbol
        )
        return name
    if isinstance(gate, (Gates.Rz, Gates.InverseRz)):
        inverse = False if isinstance(gate, Gates.Rz) else True
        name = phase_name_mpl(
            gate, "Rz", inverse, backend=backend, greek_symbol=greek_symbol
        )
        return name

    if isinstance(gate, (Gates.Rzz, Gates.InverseRzz)):
        inverse = False if isinstance(gate, Gates.Rzz) else True
        name = phase_name_mpl(
            gate, "Rzz", inverse, backend=backend, greek_symbol=greek_symbol
        )
        return name
    if isinstance(gate, (Algorithms.PCCM, Algorithms.InversePCCM)):
        inverse = False if isinstance(gate, Algorithms.PCCM) else True
        name = phase_name_mpl(
            gate,
            "PCCM",
            inverse,
            backend=backend,
            greek_symbol=greek_symbol,
            non_pccm=False,
        )
        return name

    return None


def phase_name_mpl(
    gate: QuantumOperation,
    gate_initials: str,
    inverse: bool,
    backend: Simulator,
    greek_symbol: bool,
    non_pccm: bool = True,
):
    """Return the formatted string representing a phase-related gate, for use in Matplotlib-based circuit diagrams (e.g., via `ax.text()`).

    Args:
        gate (QuantumOperation): The target phase-related gate.
        gate_initials (str): Initials or label representing the gate type (e.g., "P", "Rx") for display.
        inverse (bool): Whether the gate is an inverse variant (e.g., `InversePCCM()`, `InversePhase()`).
        backend (Simulator, optional): Backend used to resolve parameter values. Defaults to `None`.
        greek_symbol (bool, optional): Whether to convert the gate name to a Greek letter. Defaults to `True`.
        non_pccm (bool, optional): Set to `True` if the gate is not `PCCM()` or `InversePCCM()`. Defaults to `True`.

    Returns:
        str: The formatted gate label for use in the Matplotlib-rendered diagram.

    """
    name = gate.name if not isinstance(gate, Algorithms.InversePCCM) else gate.pccm.name
    string = (
        r"{}".format(gate_initials) + r"({})"
        if not inverse
        else r"{}".format(gate_initials) + r"$^\dagger$({})"
    )
    greek_string = (
        r"{}".format(gate_initials) + r"($\{}$)"
        if not inverse
        else r"{}".format(gate_initials) + r"$^\dagger$($\{}$)"
    )

    if backend is not None:
        try:
            if isinstance(backend.values[name], Symbol):
                angle = str(backend.values[name])
                angle = valid_angle(angle, non_pccm)
            else:
                angle = round(backend.values[name], 2)
            if inverse is False:
                name = f"{gate_initials} \n {angle}"
            else:
                name = f"{gate_initials}$^\\dagger$ \n {angle}"
        except KeyError:
            logger.exception("Phase angle '%s' is not specified in the backend", name)
            if greek_symbol is True:
                if name in greek_letters:
                    name = greek_string.format(name)
                else:
                    name = valid_angle(name, non_pccm)
                    name = string.format(name)
            else:
                name = valid_angle(name, non_pccm)
                name = string.format(name)
    else:
        if greek_symbol is True:
            if name in greek_letters:
                name = greek_string.format(name)
            else:
                name = valid_angle(name, non_pccm)
                name = string.format(name)
        else:
            name = valid_angle(name, non_pccm)
            name = string.format(name)
    return name
