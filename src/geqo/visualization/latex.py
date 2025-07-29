import os
import re
import subprocess
import tempfile

from IPython.display import display
from PIL import Image
from sympy import Symbol

import geqo.algorithms as Algorithms
import geqo.gates as Gates
from geqo.__logger__ import get_logger
from geqo.algorithms.algorithms import PermuteQubits, QubitReversal
from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.initialization.state import SetBits, SetDensityMatrix, SetQubits
from geqo.operations.controls import (
    ClassicalControl,
    QuantumControl,
)
from geqo.operations.measurement import DropQubits, Measure
from geqo.simulators.base import Simulator
from geqo.utils._base_.helpers import embedSequences
from geqo.visualization.common import (
    get_gate_name,
    greek_letters,
    pack_gates,
    valid_angle,
    valid_name,
)

logger = get_logger(__name__)


def phase_name(
    gate: QuantumOperation,
    string: str,
    greek_string: str,
    backend: Simulator,
    greek_symbol: bool,
    non_pccm: bool = True,
):
    r"""Return the correct LaTeX string format of the name of a phase-related gate,
    used in the quantikz command like `\\gate{gate_name}`.

    Args:
        gate (QuantumOperation): The target phase-related gate.
        string (str): The LaTeX string template (e.g., `r"P({})"`) for formatting the gate name.
        greek_string (str): A template string that turns `gate.name` into a Greek letter
            in LaTeX (e.g., `r"P(\\{})"` or `r"Rx($\\{}$)"`).
        backend (Simulator): The simulator instance that might store the phase value.
        greek_symbol (bool): Whether to convert `gate.name` into a Greek letter.
        non_pccm (bool, optional): Set to `True` if the gate is not `PCCM()` or `InversePCCM()`. Defaults to `True`.

    Returns:
        str: The formatted LaTeX string for use in quantikz diagrams.

    """
    name = gate.name if not isinstance(gate, Algorithms.InversePCCM) else gate.pccm.name

    if backend is not None:
        try:  # if backend exists, try retrieving the assinged phase value
            if isinstance(backend.values[name], Symbol):
                symbol = str(backend.values[name])
                if re.search(
                    r"[^a-zA-Z0-9 _\-]", symbol
                ):  # if the resulting name is not the regular text accepted by quantikz (i.e. θ)
                    symbol = name
                if (symbol in greek_letters) and (greek_symbol):
                    name = greek_string.format(symbol)
                else:
                    name = valid_angle(symbol, non_pccm)
                    name = string.format(name)
            else:
                angle = round(backend.values[name], 2)
                name = string.format(angle)
        except KeyError:
            logger.exception("Phase angle '%s' is not specified in the backend", name)
            if greek_symbol is True:
                if name in greek_letters:  # if gate.name is a valid greek letter
                    name = greek_string.format(name)
                else:  # if gate.name is not a valid greek letter
                    name = valid_angle(name, non_pccm)
                    name = string.format(name)
            else:
                name = valid_angle(name, non_pccm)
                name = string.format(name)
    else:  # backend does not exist
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


def tolatex(
    seq: Sequence,
    backend: Simulator = None,
    decompose_subseq: bool = False,
    pack=True,
    fold: int = 9,
    greek_symbol: bool = True,
    **kwargs,
) -> str:
    """Convert a `Sequence` object into LaTeX quantikz code for visualizing quantum circuits.

    Args:
        seq (Sequence): The geqo Sequence to convert.
        backend (Simulator, optional): The simulator instance used for resolving symbolic or numeric values in the circuit.
        decompose_subseq (bool, optional): Whether to decompose any subsequences inside the main sequence. Defaults to `False`.
        pack (bool, optional): Whether to compactify the circuit by placing non-conflicting operations in the same column. Defaults to `True`.
        fold (int, optional): The maximum number of columns to display before folding the circuit. Defaults to 9.
        greek_symbol (bool, optional): Whether to convert gate names into Greek letters. Defaults to `True`.
        **kwargs: Additional styling parameters for customizing the output.

    Returns:
        str: The LaTeX (quantikz) code representing the circuit diagram.

    """
    # decompose the subsequences if requested
    if decompose_subseq:
        seq = embedSequences(seq)

    bits = seq.bits
    qubits = seq.qubits

    operations = []
    for op in seq.gatesAndTargets:
        if isinstance(op[0], ClassicalControl):
            ctrl_bits = op[1][: len(op[0].onoff)]
            target_qubits = op[1][len(op[0].onoff) :]
            int_ctargets = [
                target if type(target) is int else seq.bits.index(target)
                for target in ctrl_bits
            ]
            int_qtargets = [
                target if type(target) is int else seq.qubits.index(target)
                for target in target_qubits
            ]
            int_targets = int_ctargets + int_qtargets
        else:
            int_targets = [
                target if type(target) is int else seq.qubits.index(target)
                for target in op[1]
            ]

        if len(op) == 2:  # non measurement
            operations.append((op[0], int_targets))
        else:  # measurement
            int_ctargets = [
                target if type(target) is int else bits.index(target)
                for target in op[2]
            ]
            operations.append((op[0], int_targets, int_ctargets))

    # compactify the sequence into columns for visualization if requested
    if pack:
        columns = pack_gates(operations)
    else:
        columns = [
            [op] for op in operations
        ]  # each column contains one operation if not packed.

    # set up styling parameters
    gate_style = f"style={{draw={kwargs.get('edgecolor', 'black')},fill={kwargs.get('facecolor', 'white')}!{kwargs.get('facecolor_intensity', '20')}}},label style={kwargs.get('gate_label_color', 'black')}"
    target_label_style = f"label style={kwargs.get('target_label_color', 'black')}"
    measure_style = f"style={{draw={kwargs.get('measure_edgecolor', 'black')},fill={kwargs.get('measure_facecolor', 'white')}!{kwargs.get('facecolor_intensity', '20')}}}"

    # initialize the list for storing constituent quantikz code strings, starting with setting the global styling.
    circuit = [
        f"\\begin{{quantikz}}[color={kwargs.get('edgecolor', 'black')},background color={kwargs.get('facecolor', 'white')}]"
    ]

    # calculate the number of circuit rows given the fold value
    if len(columns) % fold == 0:
        num_rows = len(columns) // fold
    else:
        num_rows = len(columns) // fold + 1

    # iterate over each circuit row
    for row in range(num_rows):
        # wrap up all the qubit wires in a dictionary, with each qubit wire's quantikz commands stored in a list
        # lines = {q: [f"\\lstick{{$q_{q}$}}&"] for q in range(len(qubits))}
        lines = {q: [f"\\lstick{{${qname}$}}&"] for q, qname in enumerate(qubits)}

        # calculate the number of columns included in a row
        if row < len(columns) // fold:
            num = fold
        else:
            num = len(columns) % fold

        # iterate over each column in the given row
        for column_index in range(row * fold, row * fold + num):
            targets = [
                pair[1] for idx, pair in enumerate(columns[column_index])
            ]  # target qubits of a certain column
            gates = [
                pair[0] for idx, pair in enumerate(columns[column_index])
            ]  # gates applied to a certain column
            measures = [
                pair[2] if isinstance(pair[0], Measure) else None
                for pair in columns[column_index]
            ]

            # non-targeted qubits
            nontargets = list(
                set([qubits.index(q) for q in qubits])
                - set([qubit for subtargets in targets for qubit in subtargets])
            )
            for n in nontargets:
                lines[n].append(
                    r"\qw &"
                )  # insert empty quantum wire for non-targeted qubits

            for i in range(
                len(columns[column_index])
            ):  # iterate over all the operations in the same column
                if len(targets[i]) == 1:  # single-qubit gate
                    if isinstance(
                        gates[i], (BasicGate, InverseBasicGate, Sequence)
                    ):  # self-defined gate or Sequence
                        valid_name(gates[i].name)  # check if the name is valid
                        name = gates[i].name
                        name = r"{}".format(name)
                        lines[targets[i][0]].append(
                            f"\\gate[{gate_style}]{{{name}}}&"
                        )  # append the self-defined single-qubit gate

                    if isinstance(gates[i], QuantumOperation) and not isinstance(
                        gates[i], (BasicGate, InverseBasicGate, Sequence)
                    ):  # single-qubit geqo gates defined in geqo_gates.py
                        # specify the name formats of phase-related gates and S-gate, then append the resulting gates to the quantum wires
                        if isinstance(gates[i], (Gates.SGate, Gates.InverseSGate)):
                            name = (
                                r"S"
                                if isinstance(gates[i], Gates.SGate)
                                else r"S^\dagger"
                            )
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )
                        elif isinstance(gates[i], (Gates.Phase, Gates.InversePhase)):
                            string = (
                                r"P({})"
                                if isinstance(gates[i], Gates.Phase)
                                else r"P^\dagger({})"
                            )
                            greek_string = (
                                r"P(\{})"
                                if isinstance(gates[i], Gates.Phase)
                                else r"P^\dagger(\{})"
                            )
                            name = phase_name(
                                gates[i],
                                string,
                                greek_string,
                                backend,
                                greek_symbol,
                            )
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )
                        elif isinstance(gates[i], (Gates.Rx, Gates.InverseRx)):
                            string = (
                                r"Rx({})"
                                if isinstance(gates[i], Gates.Rx)
                                else r"Rx^\dagger({})"
                            )
                            greek_string = (
                                r"Rx(\{})"
                                if isinstance(gates[i], Gates.Rx)
                                else r"Rx^\dagger(\{})"
                            )
                            name = phase_name(
                                gates[i],
                                string,
                                greek_string,
                                backend,
                                greek_symbol,
                            )
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )
                        elif isinstance(gates[i], (Gates.Ry, Gates.InverseRy)):
                            string = (
                                r"Ry({})"
                                if isinstance(gates[i], Gates.Ry)
                                else r"Ry^\dagger({})"
                            )
                            greek_string = (
                                r"Ry(\{})"
                                if isinstance(gates[i], Gates.Ry)
                                else r"Ry^\dagger(\{})"
                            )
                            name = phase_name(
                                gates[i],
                                string,
                                greek_string,
                                backend,
                                greek_symbol,
                            )
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )
                        elif isinstance(gates[i], (Gates.Rz, Gates.InverseRz)):
                            string = (
                                r"Rz({})"
                                if isinstance(gates[i], Gates.Rz)
                                else r"Rz^\dagger({})"
                            )
                            greek_string = (
                                r"Rz(\{})"
                                if isinstance(gates[i], Gates.Rz)
                                else r"Rz^\dagger(\{})"
                            )
                            name = phase_name(
                                gates[i],
                                string,
                                greek_string,
                                backend,
                                greek_symbol,
                            )
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )

                        elif isinstance(gates[i], Measure):
                            lines[targets[i][0]].append(
                                f"\\meter[{measure_style}]{{{measures[i][0]}}}&"
                            )

                        elif isinstance(gates[i], DropQubits):
                            lines[targets[i][0]].append(
                                f"\\push{{\\text{{\\Large \\textcolor{{{kwargs.get('edgecolor', 'black')}}}{{X}}}}}}&"
                            )

                        elif isinstance(gates[i], SetBits):
                            if backend is not None:
                                name = gates[i].name
                                try:
                                    bits = backend.values[name]
                                    bit = bits[0]
                                    lines[targets[i][0]].append(
                                        f"\\push{{\\textcolor{{{kwargs.get('edgecolor', 'black')}}}{{\\textcircled{{\\raisebox{{-0.2ex}}{{{bit}}}}}}}}}&"
                                    )
                                except KeyError:
                                    logger.exception(
                                        "SetBits value for '%s' is not specified in the backend",
                                        name,
                                    )
                                    lines[targets[i][0]].append(
                                        f"\\gate[{gate_style}]{{{name}}}&"
                                    )

                            else:
                                lines[targets[i][0]].append(
                                    f"\\gate[{gate_style}]{{{gates[i].name}}}&"
                                )

                        elif isinstance(gates[i], SetQubits):
                            if backend is not None:
                                name = gates[i].name
                                try:
                                    bits = backend.values[name]
                                    bit = bits[0]
                                    lines[targets[i][0]].append(
                                        f"\\push{{\\text{{\\Large \\textcolor{{{kwargs.get('edgecolor', 'black')}}}{{$\\ket{{{bit}}}$}}}}}}&"
                                    )
                                except KeyError:
                                    logger.exception(
                                        "SetQubits value for '%s' is not specified in the backend",
                                        name,
                                    )
                                    lines[targets[i][0]].append(
                                        f"\\gate[{gate_style}]{{{name}}}&"
                                    )

                            else:
                                lines[targets[i][0]].append(
                                    f"\\gate[{gate_style}]{{{gates[i].name}}}&"
                                )

                        elif isinstance(gates[i], SetDensityMatrix):
                            name = r"\rho[{}]".format(gates[i].name)
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )

                        else:
                            name = get_gate_name(gates[i])
                            lines[targets[i][0]].append(
                                f"\\gate[{gate_style}]{{{name}}}&"
                            )

                else:  # multi-qubit gates (controlled/ non-controlled)
                    if isinstance(
                        gates[i], (BasicGate, InverseBasicGate, Sequence)
                    ):  # multi-qubit self-defined gate or Sequence
                        valid_name(gates[i].name)
                        name = gates[i].name

                        for qubit in list(range(min(targets[i]), max(targets[i]) + 1)):
                            if qubit == min(targets[i]):
                                lines[qubit].append(
                                    f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                )
                            else:
                                if qubit in targets[i]:
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                    )

                    if (
                        isinstance(gates[i], (QuantumControl, ClassicalControl))
                        and not isinstance(
                            gates[i].qop,
                            (
                                Gates.SwapQubits,
                                Gates.CNOT,
                                Gates.Toffoli,
                                QuantumControl,
                            ),
                        )
                    ):  # multi-controlled gates (excluding CSwap CNOT, Toffoli, and QuantumControl)
                        onoff = gates[i].onoff
                        gate = gates[i].qop

                        if isinstance(
                            gate,
                            (
                                Measure,
                                SetBits,
                                SetQubits,
                                SetDensityMatrix,
                                ClassicalControl,
                                DropQubits,
                            ),
                        ):
                            raise TypeError(
                                "Non-unitary operations are not eligible targets for Quantum or ClassicalControl"
                            )

                        elif isinstance(gate, (BasicGate, InverseBasicGate, Sequence)):
                            name = gate.name
                            valid_name(name)

                        else:  # geqo gates defined in geqo_gates.py
                            if isinstance(gate, (Gates.SGate, Gates.InverseSGate)):
                                if isinstance(gates[i], QuantumControl):
                                    name = (
                                        r"S"
                                        if isinstance(gate, Gates.SGate)
                                        else r"S^\dagger"
                                    )
                                else:  # ClassicalControl syntax is different.
                                    name = (
                                        r"S"
                                        if isinstance(gate, Gates.SGate)
                                        else r"S$^\dagger$"
                                    )
                            elif isinstance(gate, (Gates.Phase, Gates.InversePhase)):
                                if isinstance(gates[i], QuantumControl):
                                    string = (
                                        r"P({})"
                                        if isinstance(gate, Gates.Phase)
                                        else r"P^\dagger({})"
                                    )
                                    greek_string = (
                                        r"P(\{})"
                                        if isinstance(gate, Gates.Phase)
                                        else r"P^\dagger(\{})"
                                    )
                                else:  # ClassicalControl
                                    string = (
                                        r"P({})"
                                        if isinstance(gate, Gates.Phase)
                                        else r"P^$\dagger$({})"
                                    )
                                    greek_string = (
                                        r"P($\{}$)"
                                        if isinstance(gate, Gates.Phase)
                                        else r"P^$\dagger$($\{}$)"
                                    )
                                name = phase_name(
                                    gate,
                                    string,
                                    greek_string,
                                    backend,
                                    greek_symbol,
                                )
                            elif isinstance(gate, (Gates.Rx, Gates.InverseRx)):
                                if isinstance(gates[i], QuantumControl):
                                    string = (
                                        r"Rx({})"
                                        if isinstance(gate, Gates.Rx)
                                        else r"Rx^\dagger({})"
                                    )
                                    greek_string = (
                                        r"Rx(\{})"
                                        if isinstance(gate, Gates.Rx)
                                        else r"Rx^\dagger(\{})"
                                    )
                                else:
                                    string = (
                                        r"Rx({})"
                                        if isinstance(gate, Gates.Rx)
                                        else r"Rx$^\dagger$({})"
                                    )
                                    greek_string = (
                                        r"Rx($\{}$)"
                                        if isinstance(gate, Gates.Rx)
                                        else r"Rx$^\dagger$($\{}$)"
                                    )
                                name = phase_name(
                                    gate,
                                    string,
                                    greek_string,
                                    backend,
                                    greek_symbol,
                                )
                            elif isinstance(gate, (Gates.Ry, Gates.InverseRy)):
                                if isinstance(gates[i], QuantumControl):
                                    string = (
                                        r"Ry({})"
                                        if isinstance(gate, Gates.Ry)
                                        else r"Ry^\dagger({})"
                                    )
                                    greek_string = (
                                        r"Ry(\{})"
                                        if isinstance(gate, Gates.Ry)
                                        else r"Ry^\dagger(\{})"
                                    )
                                else:
                                    string = (
                                        r"Ry({})"
                                        if isinstance(gate, Gates.Ry)
                                        else r"Ry$^\dagger$({})"
                                    )
                                    greek_string = (
                                        r"Ry($\{}$)"
                                        if isinstance(gate, Gates.Ry)
                                        else r"Ry^$\dagger$($\{}$)"
                                    )
                                name = phase_name(
                                    gate,
                                    string,
                                    greek_string,
                                    backend,
                                    greek_symbol,
                                )
                            elif isinstance(gate, (Gates.Rz, Gates.InverseRz)):
                                if isinstance(gates[i], QuantumControl):
                                    string = (
                                        r"Rz({})"
                                        if isinstance(gate, Gates.Rz)
                                        else r"Rz^\dagger({})"
                                    )
                                    greek_string = (
                                        r"Rz(\{})"
                                        if isinstance(gate, Gates.Rz)
                                        else r"Rz^\dagger(\{})"
                                    )
                                else:
                                    string = (
                                        r"Rz({})"
                                        if isinstance(gate, Gates.Rz)
                                        else r"Rz$^\dagger$({})"
                                    )
                                    greek_string = (
                                        r"Rz($\{}$)"
                                        if isinstance(gate, Gates.Rz)
                                        else r"Rz$^\dagger$($\{}$)"
                                    )
                                name = phase_name(
                                    gate,
                                    string,
                                    greek_string,
                                    backend,
                                    greek_symbol,
                                )

                            elif isinstance(
                                gate, (Gates.Rzz, Gates.InverseRzz)
                            ):  # multi-qubit target has different syntax (math mode must be enclosed in $$)
                                string = (
                                    r"Rzz({})"
                                    if isinstance(gate, Gates.Rzz)
                                    else r"Rzz$^\dagger$({})"
                                )
                                greek_string = (
                                    r"Rzz($\{}$)"
                                    if isinstance(gate, Gates.Rzz)
                                    else r"Rzz$^\dagger$($\{}$)"
                                )
                                name = phase_name(
                                    gate,
                                    string,
                                    greek_string,
                                    backend,
                                    greek_symbol,
                                )
                            elif isinstance(
                                gate, (Algorithms.PCCM, Algorithms.InversePCCM)
                            ):
                                string = (
                                    r"PCCM({})"
                                    if isinstance(gate, Algorithms.PCCM)
                                    else r"PCCM$^\dagger$({})"
                                )
                                greek_string = (
                                    r"PCCM($\{}$)"
                                    if isinstance(gate, Algorithms.PCCM)
                                    else r"PCCM$^\dagger$($\{}$)"
                                )
                                name = phase_name(
                                    gate,
                                    string,
                                    greek_string,
                                    backend,
                                    greek_symbol,
                                    non_pccm=False,
                                )

                            else:  # Other geqo gates (QubitReversal,QFT,InverseQFT,PermuteQubits)
                                name = get_gate_name(gate, backend, greek_symbol)

                        num_targets = gate.getNumberQubits()
                        target_qubits = targets[i][-num_targets:]
                        ctrl_qubits = targets[i][:-num_targets]

                        if isinstance(gate, PermuteQubits):
                            perm = gate.targetOrder
                            permq_label = {}
                            for j in range(len(perm)):
                                permq_label[target_qubits[perm[j]]] = (
                                    f"${seq.qubits[target_qubits[j]]}$"
                                )

                        order = sorted(
                            targets[i]
                        )  # sort the controlled and target qubits from top to bottom

                        if num_targets == 1:  # single target
                            if isinstance(gates[i], QuantumControl):
                                for index, qubit in enumerate(order):
                                    if (
                                        qubit < targets[i][-1]
                                    ):  # controlled qubits before the target qubit
                                        if (
                                            onoff[targets[i].index(qubit)] == 0
                                        ):  # controlled on |0> state
                                            lines[qubit].append(
                                                f"\\octrl{{{order[index + 1] - order[index]}}}&"
                                            )
                                        else:  # controlled on |1> state
                                            lines[qubit].append(
                                                f"\\ctrl{{{order[index + 1] - order[index]}}}&"
                                            )

                                    elif qubit == targets[i][-1]:  # target qubit
                                        if not isinstance(gates[i].qop, Gates.PauliX):
                                            lines[qubit].append(
                                                f"\\gate[{gate_style}]{{{name}}}&"
                                            )
                                        else:
                                            lines[qubit].append(r"\targ{}&")

                                    else:  # controlled qubits after the target qubit
                                        if (
                                            onoff[targets[i].index(qubit)] == 0
                                        ):  # controlled on |0> state
                                            lines[qubit].append(
                                                f"\\octrl{{{order[index - 1] - order[index]}}}&"
                                            )
                                        else:  # controlled on |1> state
                                            lines[qubit].append(
                                                f"\\ctrl{{{order[index - 1] - order[index]}}}&"
                                            )
                            else:  # ClassicalControl
                                for qubit in list(
                                    range(min(targets[i]), max(targets[i]) + 1)
                                ):
                                    if (
                                        qubit == min(targets[i])
                                        and qubit in target_qubits
                                        and qubit in ctrl_qubits
                                    ):
                                        lines[qubit].append(
                                            # f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{0}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[4.5em]{{{name}}}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                        )
                                    elif (
                                        qubit == min(targets[i])
                                        and qubit in target_qubits
                                    ):
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{0}}&"
                                        )
                                    elif (
                                        qubit == min(targets[i])
                                        and qubit in ctrl_qubits
                                    ):
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[targets[i][:-1].index(qubit)]}}}}}}}&"
                                        )

                                    # elif (
                                    #    qubit in target_qubits and qubit in ctrl_qubits
                                    # ):
                                    #    lines[qubit].append(
                                    #        f"\\qw \\gateinput[{target_label_style}]{{0}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    #    )
                                    elif (
                                        qubit in target_qubits
                                    ):  # qubit that the unitary gate acts on
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{0}}&"
                                        )
                                    else:
                                        if (
                                            qubit in ctrl_qubits
                                        ):  # classical control bits
                                            lines[qubit].append(
                                                f"\\qw \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                            )

                        else:  # multiple targets
                            if isinstance(gates[i], QuantumControl):
                                for index, qubit in enumerate(order):
                                    if qubit < min(
                                        target_qubits
                                    ):  # controlled qubits before the target qubit
                                        if (
                                            onoff[targets[i].index(qubit)] == 0
                                        ):  # controlled on |0> state
                                            lines[qubit].append(
                                                f"\\octrl{{{order[index + 1] - order[index]}}}&"
                                            )
                                        else:  # controlled on |1> state
                                            lines[qubit].append(
                                                f"\\ctrl{{{order[index + 1] - order[index]}}}&"
                                            )

                                    if qubit == min(
                                        target_qubits
                                    ):  # first target qubit
                                        width = (
                                            8.5
                                            if isinstance(
                                                gate,
                                                (
                                                    Algorithms.PCCM,
                                                    Algorithms.InversePCCM,
                                                ),
                                            )
                                            else 3.5
                                        )
                                        if isinstance(gate, PermuteQubits):
                                            width = 6
                                        target_label = (
                                            permq_label[qubit]
                                            if isinstance(gate, PermuteQubits)
                                            else target_qubits.index(qubit)
                                        )
                                        lines[qubit].append(
                                            f"\\gate[{max(target_qubits) - min(target_qubits) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}&"
                                        )

                                    if (
                                        min(target_qubits) < qubit <= max(target_qubits)
                                    ):  # other qubits within the target gate
                                        if qubit in target_qubits:  # target qubits
                                            target_label = (
                                                permq_label[qubit]
                                                if isinstance(gate, PermuteQubits)
                                                else target_qubits.index(qubit)
                                            )
                                            lines[qubit].append(
                                                f"\\qw \\gateinput[{target_label_style}]{{{target_label}}} &"
                                            )
                                        else:  # controlled qubits
                                            if onoff[targets[i].index(qubit)] == 0:
                                                lines[qubit].append(
                                                    r"\qw \gateinput{$\circ$} &"
                                                )
                                            else:
                                                lines[qubit].append(
                                                    r"\qw \gateinput{$\bullet$} &"
                                                )

                                    if qubit > max(
                                        target_qubits
                                    ):  # controlled qubits after the target qubit
                                        if (
                                            onoff[targets[i].index(qubit)] == 0
                                        ):  # controlled on |0> state
                                            lines[qubit].append(
                                                f"\\octrl{{{order[index - 1] - order[index]}}}&"
                                            )
                                        else:  # controlled on |1> state
                                            lines[qubit].append(
                                                f"\\ctrl{{{order[index - 1] - order[index]}}}&"
                                            )
                            else:  # ClassicalControl
                                for qubit in list(
                                    range(min(targets[i]), max(targets[i]) + 1)
                                ):
                                    width = (
                                        8.5
                                        if isinstance(
                                            gate,
                                            (
                                                Algorithms.PCCM,
                                                Algorithms.InversePCCM,
                                            ),
                                        )
                                        else 3.5
                                    )
                                    if (
                                        qubit == min(targets[i])
                                        and qubit in target_qubits
                                        and qubit in ctrl_qubits
                                    ):  # qubit index is both presented in the control bits and the target qubits
                                        target_label = (
                                            permq_label[qubit]
                                            if isinstance(gate, PermuteQubits)
                                            else target_qubits.index(qubit)
                                        )
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                        )
                                    elif (
                                        qubit == min(targets[i])
                                        and qubit in target_qubits
                                    ):
                                        target_label = (
                                            permq_label[qubit]
                                            if isinstance(gate, PermuteQubits)
                                            else target_qubits.index(qubit)
                                        )
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}&"
                                        )
                                    elif (
                                        qubit == min(targets[i])
                                        and qubit in ctrl_qubits
                                    ):
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                        )

                                    elif (
                                        qubit in target_qubits and qubit in ctrl_qubits
                                    ):  # qubit index is both presented in the control bits and the target qubits
                                        target_label = (
                                            permq_label[qubit]
                                            if isinstance(gate, PermuteQubits)
                                            else target_qubits.index(qubit)
                                        )
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{{target_label}}} \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                        )

                                    elif (
                                        qubit in target_qubits
                                    ):  # qubit that the unitary gate acts on
                                        target_label = (
                                            permq_label[qubit]
                                            if isinstance(gate, PermuteQubits)
                                            else target_qubits.index(qubit)
                                        )
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{{target_label}}}&"
                                        )
                                    else:
                                        if (
                                            qubit in ctrl_qubits
                                        ):  # classical control bits
                                            lines[qubit].append(
                                                f"\\qw \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                            )

                    if isinstance(
                        gates[i], (QuantumControl, ClassicalControl)
                    ) and isinstance(
                        gates[i].qop, (Gates.CNOT, Gates.Toffoli)
                    ):  # controlled-CNOT and Toffoli
                        onoff = gates[i].onoff
                        gate = gates[i].qop
                        num_targets = gate.getNumberQubits()
                        target_qubits = targets[i][-num_targets:]
                        ctrl_qubits = targets[i][:-num_targets]

                        order = sorted(targets[i])
                        onoff2 = list(onoff) + [1] * (gate.getNumberQubits() - 1)
                        if isinstance(gates[i], QuantumControl):
                            for index, qubit in enumerate(order):
                                if (
                                    qubit < targets[i][-1]
                                ):  # controlled qubits before the target qubit
                                    if (
                                        onoff2[targets[i].index(qubit)] == 0
                                    ):  # controlled on |0> state
                                        lines[qubit].append(
                                            f"\\octrl{{{order[index + 1] - order[index]}}}&"
                                        )
                                    else:  # controlled on |1> state
                                        lines[qubit].append(
                                            f"\\ctrl{{{order[index + 1] - order[index]}}}&"
                                        )

                                elif qubit == targets[i][-1]:  # target qubit
                                    lines[qubit].append(r"\targ{}&")

                                else:  # controlled qubits after the target qubit
                                    if (
                                        onoff2[targets[i].index(qubit)] == 0
                                    ):  # controlled on |0> state
                                        lines[qubit].append(
                                            f"\\octrl{{{order[index - 1] - order[index]}}}&"
                                        )
                                    else:  # controlled on |1> state
                                        lines[qubit].append(
                                            f"\\ctrl{{{order[index - 1] - order[index]}}}&"
                                        )
                        # raise TypeError(
                        # "CNOT and Toffoli are not eligible targets for Quantum or ClassicalControl. Please define a mulit-controlled X gate instead."
                        # )
                        else:  # ClassicalControl CNOT and Toffoli
                            name = (
                                "CX" if isinstance(gates[i].qop, Gates.CNOT) else "CCX"
                            )
                            for qubit in list(
                                range(min(targets[i]), max(targets[i]) + 1)
                            ):
                                width = 3.5
                                if (
                                    qubit == min(targets[i])
                                    and qubit in target_qubits
                                    and qubit in ctrl_qubits
                                ):  # qubit index is both presented in the control bits and the target qubits
                                    target_label = target_qubits.index(qubit)
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    )
                                elif (
                                    qubit == min(targets[i]) and qubit in target_qubits
                                ):
                                    target_label = target_qubits.index(qubit)
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}&"
                                    )
                                elif qubit == min(targets[i]) and qubit in ctrl_qubits:
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in target_qubits and qubit in ctrl_qubits
                                ):  # qubit index is both presented in the control bits and the target qubits
                                    target_label = target_qubits.index(qubit)
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{target_label}}} \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in target_qubits
                                ):  # qubit that the unitary gate acts on
                                    target_label = target_qubits.index(qubit)
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{target_label}}}&"
                                    )
                                else:
                                    if qubit in ctrl_qubits:  # classical control bits
                                        lines[qubit].append(
                                            f"\\qw \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                        )

                    if (
                        isinstance(gates[i], (QuantumControl, ClassicalControl))
                        and isinstance(gates[i].qop, QuantumControl)
                    ):  # quantum controlled-QuantumControl and classically controlled-QuantumControl
                        if isinstance(gates[i], QuantumControl):
                            onoff = gates[i].onoff
                            gate = gates[i].qop
                            onoff1 = gate.onoff
                            onoff = onoff + onoff1
                            gate = gate.qop  # unitary gate of the inner QuantumControl
                            num_targets = gate.getNumberQubits()
                            target_qubits = targets[i][-num_targets:]
                            ctrl_qubits = targets[i][:-num_targets]

                            if isinstance(gate, PermuteQubits):
                                perm = gate.targetOrder
                                permq_label = {}
                                for j in range(len(perm)):
                                    permq_label[target_qubits[perm[j]]] = (
                                        f"${seq.qubits[target_qubits[j]]}$"
                                    )

                            order = sorted(targets[i])
                            name = (
                                get_gate_name(gate, backend, greek_symbol)
                                if not isinstance(gate, (BasicGate, InverseBasicGate))
                                else gate.name
                            )
                            logger.info("name: %s gate: %s, name, gate")
                            if "\n" in name:
                                parts = name.split("\n")
                                gate_initials = parts[0].strip()
                                angle = parts[1].strip()
                                name = f"{gate_initials}({angle})"
                            for index, qubit in enumerate(order):
                                if qubit < min(
                                    target_qubits
                                ):  # controlled qubits before the target qubit
                                    if (
                                        onoff[targets[i].index(qubit)] == 0
                                    ):  # controlled on |0> state
                                        lines[qubit].append(
                                            f"\\octrl{{{order[index + 1] - order[index]}}}&"
                                        )
                                    else:  # controlled on |1> state
                                        lines[qubit].append(
                                            f"\\ctrl{{{order[index + 1] - order[index]}}}&"
                                        )

                                if qubit == min(target_qubits):  # first target qubit
                                    width = (
                                        8.5
                                        if isinstance(
                                            gate,
                                            (
                                                Algorithms.PCCM,
                                                Algorithms.InversePCCM,
                                            ),
                                        )
                                        else 3.5
                                    )
                                    if isinstance(gate, PermuteQubits):
                                        width = 6
                                    target_label = (
                                        permq_label[qubit]
                                        if isinstance(gate, PermuteQubits)
                                        else target_qubits.index(qubit)
                                    )
                                    if num_targets > 1:
                                        lines[qubit].append(
                                            f"\\gate[{max(target_qubits) - min(target_qubits) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}&"
                                        )
                                    else:  # single target
                                        lines[qubit].append(
                                            f"\\gate[{1},{gate_style}]{{\\makebox[{1}em]{{{name}}}}}&"
                                        )

                                if (
                                    min(target_qubits) < qubit <= max(target_qubits)
                                ):  # other qubits within the target gate
                                    if qubit in target_qubits:  # target qubits
                                        target_label = (
                                            permq_label[qubit]
                                            if isinstance(gate, PermuteQubits)
                                            else target_qubits.index(qubit)
                                        )
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{{target_label}}} &"
                                        )
                                    else:  # controlled qubits
                                        if onoff[targets[i].index(qubit)] == 0:
                                            lines[qubit].append(
                                                r"\qw \gateinput{$\circ$} &"
                                            )
                                        else:
                                            lines[qubit].append(
                                                r"\qw \gateinput{$\bullet$} &"
                                            )

                                if qubit > max(
                                    target_qubits
                                ):  # controlled qubits after the target qubit
                                    if (
                                        onoff[targets[i].index(qubit)] == 0
                                    ):  # controlled on |0> state
                                        lines[qubit].append(
                                            f"\\octrl{{{order[index - 1] - order[index]}}}&"
                                        )
                                    else:  # controlled on |1> state
                                        lines[qubit].append(
                                            f"\\ctrl{{{order[index - 1] - order[index]}}}&"
                                        )
                        else:  # ClassicalControl (gates[i] is Classical Control on QuantumCOntrol)
                            onoff = gates[i].onoff  # classical control onoff
                            gate = gates[i].qop  # QuantumControl
                            onoff_q = gate.onoff  # QuantumControl onoff
                            gate = gate.qop  # unitary gate of the inner QuantumControl
                            num_targets = gate.getNumberQubits()
                            target_qubits = targets[i][-num_targets:]
                            qctrl_qubits = targets[i][
                                len(onoff) : -num_targets
                            ]  # quantum control qubits
                            cctrl_qubits = targets[i][
                                : len(onoff)
                            ]  # classical control bits

                            if isinstance(gate, PermuteQubits):
                                perm = gate.targetOrder
                                permq_label = {}
                                for j in range(len(perm)):
                                    permq_label[target_qubits[perm[j]]] = (
                                        f"${seq.qubits[target_qubits[j]]}$"
                                    )

                            order = sorted(targets[i])
                            name = (
                                get_gate_name(gate, backend, greek_symbol)
                                if not isinstance(gate, (BasicGate, InverseBasicGate))
                                else gate.name
                            )
                            if "\n" in name:
                                parts = name.split("\n")
                                gate_initials = parts[0].strip()
                                angle = parts[1].strip()
                                name = f"{gate_initials}({angle})"
                            for qubit in list(
                                range(min(targets[i]), max(targets[i]) + 1)
                            ):
                                width = (
                                    8.5
                                    if isinstance(
                                        gate,
                                        (
                                            Algorithms.PCCM,
                                            Algorithms.InversePCCM,
                                        ),
                                    )
                                    else 3.5
                                )
                                if (
                                    qubit == min(targets[i])
                                    and qubit in target_qubits
                                    and qubit in cctrl_qubits
                                ):  # qubit index is both presented in the classical control bits and the target qubits
                                    target_label = (
                                        permq_label[qubit]
                                        if isinstance(gate, PermuteQubits)
                                        else target_qubits.index(qubit)
                                    )
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[cctrl_qubits.index(qubit)]}}}}}}}&"
                                    )
                                elif (
                                    qubit == min(targets[i])
                                    and qubit in cctrl_qubits
                                    and qubit in qctrl_qubits
                                ):
                                    if onoff_q[qctrl_qubits.index(qubit)] == 0:
                                        ctrl_condition = r"$\circ$"
                                    else:
                                        ctrl_condition = r"$\bullet$"
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{ctrl_condition}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[cctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit == min(targets[i]) and qubit in target_qubits
                                ):
                                    target_label = (
                                        permq_label[qubit]
                                        if isinstance(gate, PermuteQubits)
                                        else target_qubits.index(qubit)
                                    )
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_label}}}&"
                                    )
                                elif qubit == min(targets[i]) and qubit in qctrl_qubits:
                                    if onoff_q[qctrl_qubits.index(qubit)] == 0:
                                        ctrl_condition = r"$\circ$"
                                    else:
                                        ctrl_condition = r"$\bullet$"
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{ctrl_condition}}}&"
                                    )
                                elif qubit == min(targets[i]) and qubit in cctrl_qubits:
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[cctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in target_qubits and qubit in cctrl_qubits
                                ):  # qubit index is both presented in the control bits and the target qubits
                                    target_label = (
                                        permq_label[qubit]
                                        if isinstance(gate, PermuteQubits)
                                        else target_qubits.index(qubit)
                                    )
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{target_label}}} \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[cctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in qctrl_qubits and qubit in cctrl_qubits
                                ):  # qubit index is both presented in the classical control bits and the quantum control qubits
                                    if onoff_q[qctrl_qubits.index(qubit)] == 0:
                                        ctrl_condition = r"$\circ$"
                                    else:
                                        ctrl_condition = r"$\bullet$"
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{ctrl_condition}}} \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[cctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in target_qubits
                                ):  # qubit that the unitary gate acts on
                                    target_label = (
                                        permq_label[qubit]
                                        if isinstance(gate, PermuteQubits)
                                        else target_qubits.index(qubit)
                                    )
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{target_label}}}&"
                                    )
                                elif qubit in qctrl_qubits:  # control qubits
                                    if onoff_q[qctrl_qubits.index(qubit)] == 0:
                                        ctrl_condition = r"$\circ$"
                                    else:
                                        ctrl_condition = r"$\bullet$"
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{ctrl_condition}}}&"
                                    )
                                else:
                                    if qubit in cctrl_qubits:  # classical control bits
                                        lines[qubit].append(
                                            f"\\qw \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[cctrl_qubits.index(qubit)]}}}}}}}&"
                                        )

                    if isinstance(
                        gates[i], (QuantumControl, ClassicalControl)
                    ) and isinstance(
                        gates[i].qop, Gates.SwapQubits
                    ):  # controlled-swap gate
                        if isinstance(gates[i], QuantumControl):
                            onoff = gates[i].onoff

                            ctrl_qubits = targets[i][:-2]

                            order = sorted(targets[i])

                            # draw vertical line from the first to the last qubit
                            if min(targets[i]) in ctrl_qubits:
                                if onoff[ctrl_qubits.index(min(targets[i]))] == 0:
                                    lines[min(targets[i])].append(
                                        f"\\octrl{{{max(targets[i]) - min(targets[i])}}}&"
                                    )
                                else:
                                    lines[min(targets[i])].append(
                                        f"\\ctrl{{{max(targets[i]) - min(targets[i])}}}&"
                                    )
                            else:
                                lines[min(targets[i])].append(
                                    f"\\swap{{{max(targets[i]) - min(targets[i])}}}&"
                                )

                            # draw either circle or cross
                            for qubit in order[1:]:
                                if qubit in ctrl_qubits:
                                    if onoff[ctrl_qubits.index(qubit)] == 0:
                                        lines[qubit].append(r"\ocontrol{}&")
                                    else:
                                        lines[qubit].append(r"\control{}&")
                                else:
                                    lines[qubit].append("\\targX{}&")
                        else:  # ClassicalControl
                            onoff = gates[i].onoff
                            target_qubits = targets[i][-2:]
                            ctrl_qubits = targets[i][:-2]
                            name = r"SWAP"
                            width = 6
                            for qubit in list(
                                range(min(targets[i]), max(targets[i]) + 1)
                            ):
                                if (
                                    qubit == min(targets[i])
                                    and qubit in target_qubits
                                    and qubit in ctrl_qubits
                                ):  # qubit index is both presented in the control bits and the target qubits
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_qubits.index(qubit)}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    )
                                elif (
                                    qubit == min(targets[i]) and qubit in target_qubits
                                ):
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateinput[{target_label_style}]{{{target_qubits.index(qubit)}}}&"
                                    )
                                elif qubit == min(targets[i]) and qubit in ctrl_qubits:
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[{width}em]{{{name}}}}}\\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in target_qubits and qubit in ctrl_qubits
                                ):  # qubit index is both presented in the control bits and the target qubits
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{target_qubits.index(qubit)}}} \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                    )

                                elif (
                                    qubit in target_qubits
                                ):  # qubit that the unitary gate acts on
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{target_qubits.index(qubit)}}}&"
                                    )
                                else:
                                    if qubit in ctrl_qubits:  # classical control bits
                                        lines[qubit].append(
                                            f"\\qw \\gateoutput[{target_label_style}]{{\\textcircled{{\\raisebox{{-0.2ex}}{{{onoff[ctrl_qubits.index(qubit)]}}}}}}}&"
                                        )

                    if isinstance(gates[i], QuantumOperation) and not isinstance(
                        gates[i], QuantumControl
                    ):  # multi-qubit geqo gates
                        if isinstance(gates[i], Gates.CNOT):
                            lines[targets[i][0]].append(
                                f"\\ctrl{{{targets[i][-1] - targets[i][0]}}}&"
                            )
                            lines[targets[i][-1]].append(r"\targ{}&")

                        if isinstance(gates[i], Gates.Toffoli):
                            order = sorted(targets[i])

                            for index, qubit in enumerate(order):
                                if (
                                    qubit < targets[i][-1]
                                ):  # controlled qubits before the target qubit
                                    lines[qubit].append(
                                        f"\\ctrl{{{order[index + 1] - order[index]}}}&"
                                    )

                                elif qubit == targets[i][-1]:  # target qubit
                                    lines[qubit].append(r"\targ{}&")

                                else:  # controlled qubits after the target qubit
                                    lines[qubit].append(
                                        f"\\ctrl{{{order[index - 1] - order[index]}}}&"
                                    )

                        if isinstance(
                            gates[i], (Algorithms.QFT, Algorithms.InverseQFT)
                        ):
                            name = get_gate_name(gates[i])
                            for qubit in list(
                                range(min(targets[i]), max(targets[i]) + 1)
                            ):
                                if qubit == min(targets[i]):
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                    )
                                else:
                                    if qubit in targets[i]:
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                        )

                        if isinstance(gates[i], (Gates.Rzz, Gates.InverseRzz)):
                            string = (
                                r"Rzz({})"
                                if isinstance(gates[i], Gates.Rzz)
                                else r"Rzz^\dagger({})"
                            )
                            greek_string = (
                                r"Rzz(\{})"
                                if isinstance(gates[i], Gates.Rzz)
                                else r"Rzz^\dagger(\{})"
                            )
                            name = phase_name(
                                gates[i],
                                string,
                                greek_string,
                                backend,
                                greek_symbol,
                            )

                            lines[min(targets[i])].append(
                                f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{{name}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                            )
                            lines[max(targets[i])].append(
                                f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(max(targets[i]))}}}&"
                            )

                        if isinstance(
                            gates[i], (Algorithms.PCCM, Algorithms.InversePCCM)
                        ):
                            string = (
                                r"PCCM({})"
                                if isinstance(gates[i], Algorithms.PCCM)
                                else r"PCCM^\dagger({})"
                            )
                            greek_string = (
                                r"PCCM(\{})"
                                if isinstance(gates[i], Algorithms.PCCM)
                                else r"PCCM^\dagger(\{})"
                            )
                            name = phase_name(
                                gates[i],
                                string,
                                greek_string,
                                backend,
                                greek_symbol,
                                non_pccm=False,
                            )

                            lines[min(targets[i])].append(
                                f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{{name}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                            )
                            lines[max(targets[i])].append(
                                f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(max(targets[i]))}}}&"
                            )

                        if isinstance(gates[i], Measure):
                            for j in range(len(targets[i])):
                                lines[targets[i][j]].append(
                                    f"\\meter[{measure_style}]{{{measures[i][j]}}}&"
                                )

                        if isinstance(gates[i], DropQubits):
                            for qubit in targets[i]:
                                lines[qubit].append(
                                    f"\\push{{\\text{{\\Large \\textcolor{{{kwargs.get('edgecolor', 'black')}}}{{X}}}}}}&"
                                )

                        if isinstance(gates[i], SetBits):
                            name = gates[i].name
                            if backend is not None:
                                try:
                                    bits = backend.values[name]
                                    for index, bit in enumerate(bits):
                                        lines[targets[i][index]].append(
                                            f"\\push{{\\textcolor{{{kwargs.get('edgecolor', 'black')}}}{{\\textcircled{{\\raisebox{{-0.2ex}}{{{bit}}}}}}}}}&"
                                        )
                                except KeyError:
                                    logger.exception(
                                        "SetBits values for '%s' are not specified in the backend",
                                        name,
                                    )
                                    for qubit in list(
                                        range(
                                            min(targets[i]),
                                            max(targets[i]) + 1,
                                        )
                                    ):
                                        if qubit == min(targets[i]):
                                            lines[qubit].append(
                                                f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                            )
                                        else:
                                            if qubit in targets[i]:
                                                lines[qubit].append(
                                                    f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                                )
                            else:
                                for qubit in list(
                                    range(min(targets[i]), max(targets[i]) + 1)
                                ):
                                    if qubit == min(targets[i]):
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                        )
                                    else:
                                        if qubit in targets[i]:
                                            lines[qubit].append(
                                                f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                            )

                        if isinstance(gates[i], SetQubits):
                            name = gates[i].name
                            if backend is not None:
                                try:
                                    bits = backend.values[name]
                                    for index, bit in enumerate(bits):
                                        lines[targets[i][index]].append(
                                            f"\\push{{\\text{{\\Large \\textcolor{{{kwargs.get('edgecolor', 'black')}}}{{$\\ket{{{bit}}}$}}}}}}&"
                                        )
                                except KeyError:
                                    logger.exception(
                                        "SetQubits values for '%s' are not specified in the backend",
                                        name,
                                    )
                                    for qubit in list(
                                        range(
                                            min(targets[i]),
                                            max(targets[i]) + 1,
                                        )
                                    ):
                                        if qubit == min(targets[i]):
                                            lines[qubit].append(
                                                f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                            )
                                        else:
                                            if qubit in targets[i]:
                                                lines[qubit].append(
                                                    f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                                )
                            else:
                                for qubit in list(
                                    range(min(targets[i]), max(targets[i]) + 1)
                                ):
                                    if qubit == min(targets[i]):
                                        lines[qubit].append(
                                            f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                        )
                                    else:
                                        if qubit in targets[i]:
                                            lines[qubit].append(
                                                f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                            )

                        if isinstance(gates[i], SetDensityMatrix):
                            name = r"$\rho[{}]$".format(gates[i].name)
                            for qubit in list(
                                range(min(targets[i]), max(targets[i]) + 1)
                            ):
                                if qubit == min(targets[i]):
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[3.5em]{{{name}}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min(targets[i]))}}}&"
                                    )
                                else:
                                    if qubit in targets[i]:
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{{targets[i].index(qubit)}}}&"
                                        )

                        if isinstance(gates[i], Gates.SwapQubits):
                            lines[min(targets[i])].append(
                                f"\\swap{{{max(targets[i]) - min(targets[i])}}}&"
                            )
                            lines[max(targets[i])].append("\\targX{}&")

                        if isinstance(gates[i], QubitReversal):
                            min_tq, max_tq = min(targets[i]), max(targets[i])
                            num_qubits = max_tq - min_tq + 1  # Total span of the gate

                            # First qubit in the gate range gets the main gate box
                            lines[min_tq].append(
                                f"\\gate[{num_qubits},{gate_style}]{{\\makebox[3.5em]{{$\\mathbb{{R}}\\text{{vrs}}$}}}}\\gateinput[{target_label_style}]{{{targets[i].index(min_tq)}}}&"
                            )

                            # Loop over all target qubits
                            for qubit in targets[i]:
                                if qubit != min_tq:
                                    input_index = targets[i].index(qubit)
                                    lines[qubit].append(
                                        f"\\qw \\gateinput[{target_label_style}]{{{input_index}}} &"
                                    )

                        if isinstance(gates[i], PermuteQubits):
                            perm = gates[i].targetOrder
                            permq_label = {}
                            for j in range(len(perm)):
                                permq_label[targets[i][perm[j]]] = (
                                    f"${seq.qubits[targets[i][j]]}$"
                                )

                            name = get_gate_name(gates[i])
                            for qubit in list(
                                range(min(targets[i]), max(targets[i]) + 1)
                            ):
                                if qubit == min(targets[i]):
                                    lines[qubit].append(
                                        f"\\gate[{max(targets[i]) - min(targets[i]) + 1},{gate_style}]{{\\makebox[6em]{{{name}}}}}\\gateinput[{target_label_style}]{{{permq_label[qubit]}}}&"
                                    )
                                else:
                                    if qubit in targets[i]:
                                        lines[qubit].append(
                                            f"\\qw \\gateinput[{target_label_style}]{{{permq_label[qubit]}}}&"
                                        )

        # assemble circuit
        circuit.extend("".join(lines[q]) + r"\qw & \\" for q in sorted(lines.keys()))
        if row < num_rows - 1:
            circuit.append(r"\\")  # row break for a new row of circuit
    circuit.append(r"\end{quantikz}")

    return "\n".join(circuit)


def render_latex_to_image(latex_code: str, filename: str = None):
    """Render LaTeX code (quantikz) to a PDF, then convert it to a PNG image for visualization.

    Args:
        latex_code (str): The LaTeX code to render.
        filename (str, optional): If provided, the PNG image will be saved with this filename. Defaults to `None`.

    Returns:
        PIL.Image: The rendered image. Displayed inline (e.g., in Jupyter) and optionally saved as a PNG file.

    """
    if filename is None:  # circuit diagram not saved if the filename is not specified
        filename = "circuit_diagram"
        save_png = False
    else:
        save_png = True

    # create temporary files (automatically deleted afterwards)
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_filename = os.path.join(temp_dir, f"{filename}.tex")
        pdf_filename = os.path.join(temp_dir, f"{filename}.pdf")
        png_filename = os.path.join(temp_dir, f"{filename}.png")

        # wrap Latex content into a standalone document
        latex_document = f"""
        \\documentclass{{standalone}}
        \\usepackage{{quantikz}}
        \\usepackage{{amssymb}}
        \\usepackage{{xcolor}}
        \\usepackage[dvipsnames]{{xcolor}}
        \\begin{{document}}
        {latex_code}
        \\end{{document}}
        """

        # save the Latex code to a .tex file
        with open(tex_filename, "w") as f:
            f.write(latex_document)

        # render Latex to PDF (runs pdflatex twice to ensure references are resolved)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_filename],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_filename],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # convert PDF to PNG (Ghostscript)
        subprocess.run(
            [
                "gs",
                "-q",
                "-dNOPAUSE",
                "-dBATCH",
                "-sDEVICE=pngalpha",
                "-r300",
                f"-sOutputFile={png_filename}",
                pdf_filename,
            ],
            cwd=temp_dir,
        )
        logger.debug(
            "Checking if PNG exists before opening: %s", os.path.exists(png_filename)
        )

        image = Image.open(png_filename)
        display(image)

        # save PNG if the filename is specified
        if save_png:
            output_png = f"{filename}.png"
            image.save(output_png)
            logger.info("Circuit diagram saved as %s", output_png)


def plot_latex(
    seq: Sequence,
    backend: Simulator = None,
    decompose_subseq: bool = False,
    pack: bool = True,
    fold: int = 9,
    greek_symbol: bool = True,
    filename: str = None,
    return_quantikz: bool = False,
    **kwargs,
):
    """Plot a LaTeX-style (quantikz) quantum circuit diagram from a geqo `Sequence`.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        backend (Simulator, optional): The simulator backend used to resolve parameter values. Defaults to `None`.
        decompose_subseq (bool, optional): Whether to decompose subsequences within the main sequence. Defaults to `False`.
        pack (bool, optional): Whether to compactify the circuit by placing non-conflicting gates in the same column. Defaults to `True`.
        fold (int, optional): Maximum number of lines to show before folding the circuit. Defaults to 9.
        greek_symbol (bool, optional): Whether to render gate names using Greek letters. Defaults to `True`.
        filename (str, optional): If provided, the output PNG will be saved with this filename. Defaults to `None`.
        return_quantikz (bool, optional): If `True`, the quantikz LaTeX code will be returned and printed. Defaults to `False`.
        **kwargs: Additional styling options passed to the LaTeX generator.

    Returns:
        PIL.Image: The rendered quantum circuit image.
        str (optional): The LaTeX (quantikz) code, if `return_quantikz` is `True`.

    """
    latex_code = tolatex(
        seq, backend, decompose_subseq, pack, fold, greek_symbol, **kwargs
    )
    render_latex_to_image(latex_code, filename)

    if return_quantikz is True:
        return latex_code
