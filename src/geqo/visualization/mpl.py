import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

import geqo.algorithms as Algorithms
import geqo.gates as Gates
from geqo.__logger__ import get_logger
from geqo.algorithms.algorithms import PermuteQubits, QubitReversal
from geqo.core.basic import BasicGate, InverseBasicGate
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.initialization.state import SetBits, SetDensityMatrix, SetQubits
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.operations.measurement import DropQubits, Measure
from geqo.simulators.base import Simulator
from geqo.utils._base_.helpers import embedSequences
from geqo.visualization.common import get_gate_name, pack_gates, valid_name

logger = get_logger(__name__)


def draw_single_qubit_gate(
    seq: Sequence,
    gate: QuantumOperation,
    ax: Axes,
    qubits: list,
    num_qubits: int,
    i: int,
    backend: Simulator | None = None,
    greek_symbol: bool = True,
    measure_bit: list | None = None,
    **kwargs,
):
    """Plot a single-qubit gate onto a Matplotlib axis as part of a quantum circuit diagram.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        gate (QuantumOperation): The gate to plot. Can be a standard geqo gate, a user-defined gate, or a non-unitary operation (e.g., Measure, DropQubits).
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits (should have length 1 for single-qubit gates).
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where this gate should be placed.
        backend (Simulator, optional): Simulator backend used to evaluate symbolic or numeric parameters. Defaults to `None`.
        greek_symbol (bool, optional): Whether to render gate labels using Greek letters when applicable. Defaults to `True`.
        measure_bit (list, optional): The list of classical bits where the measurement results are stored. Defaults to `None`
        **kwargs: Additional keyword arguments for styling (e.g., colors, alpha transparency).

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the gate rendered.

    """
    x_pos = 1 + i
    y_pos = num_qubits - 1 - qubits[0]

    if isinstance(gate, (BasicGate, InverseBasicGate, Sequence)):  # Self-defined gates
        ax.add_patch(
            FancyBboxPatch(
                (x_pos, y_pos - 0.3),
                0.6,
                0.6,
                boxstyle="round4,pad=0.05",
                fill=True,
                facecolor=kwargs.get("basicgate_facecolor", "white"),
                edgecolor=kwargs.get("basicgate_edgecolor", "black"),
                alpha=kwargs.get("gate_alpha", 1),
                zorder=2,
            )
        )
        valid_name(gate.name)
        name = f"${gate.name}$"
        fontsize = 12

    elif isinstance(gate, QuantumOperation):  # geqo gates
        if isinstance(gate, Measure):  # Measurement gate
            ax.add_patch(
                plt.Circle(
                    (x_pos + 0.2, y_pos),
                    0.2,
                    fill=True,
                    facecolor=kwargs.get("measure_facecolor", "white"),
                    edgecolor=kwargs.get("measure_edgecolor", "black"),
                    alpha=kwargs.get("gate_alpha", 1),
                    zorder=2,
                )
            )
        elif isinstance(gate, DropQubits):
            plot_dropbits(ax, qubits, num_qubits, i, **kwargs)
        elif isinstance(gate, SetBits):
            plot_setbits(seq, gate, ax, qubits, num_qubits, i, backend, **kwargs)
        elif isinstance(gate, SetQubits):
            plot_setqubits(seq, gate, ax, qubits, num_qubits, i, backend, **kwargs)
        elif isinstance(gate, SetDensityMatrix):
            plot_setdensitymatrix(seq, gate.name, ax, qubits, num_qubits, i, **kwargs)
        else:  # Unitary gates
            ax.add_patch(
                FancyBboxPatch(
                    (x_pos, y_pos - 0.3),
                    0.6,
                    0.6,
                    boxstyle="round4,pad=0.05",
                    fill=True,
                    facecolor=kwargs.get("geqogate_facecolor", "white"),
                    edgecolor=kwargs.get("geqogate_edgecolor", "black"),
                    alpha=kwargs.get("gate_alpha", 1),
                    zorder=2,
                )
            )

        name = get_gate_name(gate, backend=backend, greek_symbol=greek_symbol)
        fontsize = 15 if isinstance(gate, (Measure, DropQubits, SetBits)) else 12

    else:
        return  # Exit if the gate type is unknown

    if not isinstance(gate, (DropQubits, SetBits, SetQubits, SetDensityMatrix)):
        xshift = 0.2 if isinstance(gate, Measure) else 0.3
        ax.text(
            x_pos + xshift,
            y_pos,
            name,
            ha="center",
            va="center",
            fontsize=fontsize,
            color=kwargs.get("text_color", "black"),
        )

    if isinstance(gate, Measure):
        # if measure_bit is None:
        # measure_bit = qubits
        ax.text(
            x_pos + 0.45,
            y_pos - 0.25,
            measure_bit[0],
            ha="center",
            va="center",
            fontsize=10,
            color=kwargs.get("wire_color", "black"),
        )


def plot_cnot(
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a CNOT gate onto a Matplotlib axis.

    Args:
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits (should have length 2 for CNOT gates).
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the CNOT should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'wire_color', 'gate_alpha').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the CNOT gate rendered.

    """
    if qubits[0] < qubits[1]:
        ax.plot(
            [i + 1 + 0.2, i + 1 + 0.2],
            [num_qubits - 1 - qubits[0], num_qubits - 1 - qubits[1] - 0.2],
            kwargs.get("wire_color", "black"),
            lw=1,
        )  # Control line
    else:
        ax.plot(
            [i + 1 + 0.2, i + 1 + 0.2],
            [num_qubits - 1 - qubits[0], num_qubits - 1 - qubits[1] + 0.2],
            kwargs.get("wire_color", "black"),
            lw=1,
        )  # Control line
    ax.plot(
        i + 1 + 0.2,
        num_qubits - 1 - qubits[0],
        marker="o",
        markerfacecolor="black",
        markeredgecolor=kwargs.get("wire_color", "black"),
        markersize=6,
    )  # Control dot
    ax.add_patch(
        plt.Circle(
            (i + 1 + 0.2, num_qubits - 1 - qubits[1]),
            0.2,
            fill=False,
            edgecolor=kwargs.get("wire_color", "black"),
        )
    )  # Target circle
    ax.plot(
        [i + 1, i + 1 + 0.4],
        [num_qubits - 1 - qubits[1], num_qubits - 1 - qubits[1]],
        kwargs.get("wire_color", "black"),
        lw=1,
    )  # Plus sign horizontal


def plot_swap(
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a SWAP gate onto a Matplotlib axis.

    Args:
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits (should have length 2 for SWAP gates).
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the SWAP should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'wire_color').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the SWAP gate rendered.

    """
    q0, q1 = qubits
    x_pos = i + 1 + 0.2
    y0, y1 = num_qubits - 1 - q0, num_qubits - 1 - q1
    ax.plot(
        [x_pos, x_pos], [y0, y1], kwargs.get("wire_color", "black"), lw=1
    )  # Control line

    for q in [q0, q1]:  # X marks at qubits
        y_q = num_qubits - 1 - q
        ax.plot(
            [i + 1 + 0.05, i + 1 + 0.35],
            [y_q - 0.15, y_q + 0.15],
            kwargs.get("wire_color", "black"),
            lw=1,
        )
        ax.plot(
            [i + 1 + 0.05, i + 1 + 0.35],
            [y_q + 0.15, y_q - 0.15],
            kwargs.get("wire_color", "black"),
            lw=1,
        )


def plot_ctrl_swap(
    ctrl_type: str,
    ax: matplotlib.axes,
    qubits: list,
    onoff: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a controlled-SWAP gate onto a Matplotlib axis.

    Args:
        ctrl_type (str): The type of control operation. Should either "quantum" (QuantumControl) or "classical" (ClassicalControl).
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        onoff (list): A list of binary values indicating the controlled states.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the controlled-SWAP should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'wire_color').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the controlled-SWAP gate rendered.

    """
    ctrl_q = qubits[:-2]
    targ_q = qubits[-2:]
    x_pos = i + 1 + 0.2
    y0, y1 = num_qubits - 1 - min(qubits), num_qubits - 1 - max(qubits)
    ax.plot(
        [x_pos, x_pos],
        [y0, y1],
        kwargs.get("wire_color", "black"),
        lw=1,
        zorder=2,
    )

    for q in qubits:
        y_q = num_qubits - 1 - q
        if q in ctrl_q:
            if ctrl_type == "quantum":
                ax.plot(
                    [x_pos],
                    [y_q],
                    marker="o",
                    markersize=6,
                    markerfacecolor="black" if onoff[ctrl_q.index(q)] else "white",
                    markeredgecolor=kwargs.get("wire_color", "black"),
                    zorder=3,
                )
            else:  # ClassicalControl
                xshift1 = (
                    0.2 if q in targ_q else 0
                )  # if the classical control bit overlaps the target qubit
                ax.add_patch(
                    plt.Circle(
                        (x_pos + xshift1, y_q),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=3,
                    )
                )
                text = onoff[ctrl_q.index(q)]
                xshift2 = 0.01 if onoff[ctrl_q.index(q)] == 0 else 0
                ax.text(
                    x_pos + xshift1 - xshift2,
                    y_q,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )
        if q in targ_q:  # q is swap target (might overlap with classical control bit)
            ax.plot(
                [i + 1 + 0.05, i + 1 + 0.35],
                [y_q - 0.15, y_q + 0.15],
                kwargs.get("wire_color", "black"),
                lw=1,
            )
            ax.plot(
                [i + 1 + 0.05, i + 1 + 0.35],
                [y_q + 0.15, y_q - 0.15],
                kwargs.get("wire_color", "black"),
                lw=1,
            )


def plot_toffoli(ax: matplotlib.axes, qubits: list, num_qubits: int, i: int, **kwargs):
    """Plot a Toffoli gate onto a Matplotlib axis.

    Args:
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits (should have length 3 for SWAP gates).
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the Toffoli gate should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'wire_color').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the Toffoli gate rendered.

    """
    order = sorted(qubits)
    for index, bit in enumerate(order):
        if bit < qubits[-1]:  # controlled qubits before the target qubit
            if order[index + 1] == qubits[-1] and order[-1] == qubits[-1]:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index + 1] - 0.2,
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            else:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index + 1],
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            ax.plot(
                i + 1 + 0.2,
                num_qubits - 1 - bit,
                marker="o",
                markerfacecolor="black",
                markeredgecolor=kwargs.get("wire_color", "black"),
                markersize=6,
                zorder=3,
            )  # control dot

        elif bit == qubits[-1]:  # target qubit
            ax.add_patch(
                plt.Circle(
                    (i + 1 + 0.2, num_qubits - 1 - bit),
                    0.2,
                    fill=False,
                    edgecolor=kwargs.get("wire_color", "black"),
                )
            )  # Target circle
            # ax.plot([i+1+0.2, i+1+0.2], [self.num_qubits-1-bit+0.2, self.num_qubits-1-bit-0.2], 'gray', lw=1)  # Plus sign vertical
            ax.plot(
                [i + 1, i + 1 + 0.4],
                [num_qubits - 1 - bit, num_qubits - 1 - bit],
                kwargs.get("wire_color", "black"),
                lw=1,
            )  # Plus sign horizontal

        else:  # controlled qubits after the target qubit
            if order[index - 1] == qubits[-1] and order[0] == qubits[-1]:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index - 1] + 0.2,
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            else:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index - 1],
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            ax.plot(
                i + 1 + 0.2,
                num_qubits - 1 - bit,
                marker="o",
                markerfacecolor="black",
                markeredgecolor=kwargs.get("wire_color", "black"),
                markersize=6,
                zorder=3,
            )  # control dot


def plot_multix(
    ctrl_type: str,
    ax: matplotlib.axes,
    qubits: list,
    onoff: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a mulit-controlled X gate onto a Matplotlib axis.

    Args:
        ctrl_type (str): The type of control operation. Should either "quantum" (QuantumControl) or "classical" (ClassicalControl).
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits (should have length 3 for SWAP gates).
        onoff (list): A list of binary values indicating the controlled states.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the Toffoli gate should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'wire_color').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the Toffoli gate rendered.

    """
    controls = qubits[:-1]
    order = sorted(qubits)
    for index, bit in enumerate(order):
        if bit < qubits[-1]:  # controlled qubits before the target qubit
            if order[index + 1] == qubits[-1] and order[-1] == qubits[-1]:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index + 1] - 0.2,
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            else:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index + 1],
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            if ctrl_type == "quantum":
                ax.plot(
                    i + 1 + 0.2,
                    num_qubits - 1 - bit,
                    marker="o",
                    markerfacecolor="black" if onoff[controls.index(bit)] else "white",
                    markeredgecolor=kwargs.get("wire_color", "black"),
                    markersize=6,
                    zorder=3,
                )  # control dot
            else:  # ClassicalControl
                ax.add_patch(
                    plt.Circle(
                        (i + 1 + 0.2, num_qubits - 1 - bit),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=3,
                    )
                )
                text = onoff[controls.index(bit)]
                xshift = 0.01 if onoff[controls.index(bit)] == 0 else 0
                ax.text(
                    i + 1 + 0.2 - xshift,
                    num_qubits - 1 - bit,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

        elif bit == qubits[-1]:  # target qubit
            ax.add_patch(
                plt.Circle(
                    (i + 1 + 0.2, num_qubits - 1 - bit),
                    0.2,
                    fill=False,
                    edgecolor=kwargs.get("wire_color", "black"),
                )
            )  # Target circle
            # ax.plot([i+1+0.2, i+1+0.2], [self.num_qubits-1-bit+0.2, self.num_qubits-1-bit-0.2], 'gray', lw=1)  # Plus sign vertical
            ax.plot(
                [i + 1, i + 1 + 0.4],
                [num_qubits - 1 - bit, num_qubits - 1 - bit],
                kwargs.get("wire_color", "black"),
                lw=1,
            )  # Plus sign horizontal

            if bit in controls:  # target qubit overlaps with the classical control bit
                # draw classical control dot close to the target qubit
                ax.add_patch(
                    plt.Circle(
                        (i + 1 + 0.45, num_qubits - 1 - bit - 0.25),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=3,
                    )
                )
                text = onoff[controls.index(bit)]
                xshift = 0.01 if onoff[controls.index(bit)] == 0 else 0
                ax.text(
                    i + 1 + 0.45 - xshift,
                    num_qubits - 1 - bit - 0.25,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

        else:  # controlled qubits after the target qubit
            if order[index - 1] == qubits[-1] and order[0] == qubits[-1]:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index - 1] + 0.2,
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            else:
                ax.plot(
                    [i + 1 + 0.2, i + 1 + 0.2],
                    [
                        num_qubits - 1 - order[index],
                        num_qubits - 1 - order[index - 1],
                    ],
                    kwargs.get("wire_color", "black"),
                    lw=1,
                )  # control line
            if ctrl_type == "quantum":
                ax.plot(
                    i + 1 + 0.2,
                    num_qubits - 1 - bit,
                    marker="o",
                    markerfacecolor="black" if onoff[controls.index(bit)] else "white",
                    markeredgecolor=kwargs.get("wire_color", "black"),
                    markersize=6,
                    zorder=3,
                )  # control dot
            else:  # ClassicalControl dot
                ax.add_patch(
                    plt.Circle(
                        (i + 1 + 0.2, num_qubits - 1 - bit),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=3,
                    )
                )
                text = onoff[controls.index(bit)]
                xshift = 0.01 if onoff[controls.index(bit)] == 0 else 0
                ax.text(
                    i + 1 + 0.2 - xshift,
                    num_qubits - 1 - bit,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )


def plot_dropbits(
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a DropQubits operation onto a Matplotlib axis.

    Args:
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the DropQubits operation should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'drop_color').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the DropQubits operation rendered.

    """
    x_pos = i + 1 + 0.3

    for qb in qubits:
        y_pos = num_qubits - 1 - qb
        ax.add_patch(
            plt.Circle(
                (x_pos, y_pos),
                radius=0.3,
                facecolor="none",
                edgecolor=kwargs.get("drop_color", "dimgray"),
                linewidth=2,
                ls="dashdot",
            )
        )
        ax.add_line(
            plt.Line2D(
                [x_pos - 0.3, x_pos + 0.3],
                [y_pos - 0.3, y_pos + 0.3],
                color=kwargs.get("drop_color", "dimgray"),
                linewidth=2,
                ls="dashdot",
            )
        )
        ax.add_line(
            plt.Line2D(
                [x_pos - 0.3, x_pos + 0.3],
                [y_pos + 0.3, y_pos - 0.3],
                color=kwargs.get("drop_color", "dimgray"),
                linewidth=2,
                ls="dashdot",
            )
        )


def plot_setbits(
    seq: Sequence,
    gate: QuantumOperation,
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    backend: Simulator | None = None,
    **kwargs,
):
    """Plot a SetBits operation onto a Matplotlib axis.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        gate (QuantumOperation): The target SetBits gate instance, whose name is used to query the assigned values from the backend.
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the SetBits operation should be placed.
        backend (Simulator, optional): Backend used to resolve symbolic or numeric parameter values. Defaults to `None`.
        **kwargs: Additional keyword arguments for styling (e.g., 'setbits_facecolor', 'setbits_edgecolor').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the SetBits operation rendered.

    """
    name = gate.name
    if backend is not None:
        try:
            bits = backend.values[name]
            for index, bit in enumerate(bits):
                ax.add_patch(
                    plt.Circle(
                        (i + 1, num_qubits - 1 - qubits[index]),
                        0.2,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                ax.text(
                    i + 1,
                    num_qubits - 1 - qubits[index],
                    bit,
                    ha="center",
                    va="center",
                    fontsize=15,
                    color=kwargs.get("text_color", "black"),
                    zorder=3,
                )

        except KeyError:
            setgate = BasicGate(name, len(qubits))
            if len(qubits) > 1:
                logger.warning(
                    "SetBits values for '%s' are not specified in the backend", name
                )
                draw_multi_qubit_gate(
                    seq,
                    setgate,
                    ax,
                    qubits,
                    num_qubits,
                    i,
                    backend=None,
                    basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                    basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                    linethrough_ls=kwargs.get("linethrough_ls", "solid"),
                    wire_color=kwargs.get("wire_color", "black"),
                    text_color=kwargs.get("text_color", "black"),
                    gate_alpha=kwargs.get("gate_alpha", 1),
                )
            else:  # single qubit setbits
                logger.warning(
                    "SetBits value for '%s' is not specified in the backend", name
                )
                draw_single_qubit_gate(
                    seq,
                    setgate,
                    ax,
                    qubits,
                    num_qubits,
                    i,
                    backend=None,
                    greek_symbol=True,
                    basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                    basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                    text_color=kwargs.get("text_color", "black"),
                    gate_alpha=kwargs.get("gate_alpha", 1),
                )
    else:
        setgate = BasicGate(name, len(qubits))
        if len(qubits) > 1:
            draw_multi_qubit_gate(
                seq,
                setgate,
                ax,
                qubits,
                num_qubits,
                i,
                backend=None,
                basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                linethrough_ls=kwargs.get("linethrough_ls", "solid"),
                wire_color=kwargs.get("wire_color", "black"),
                text_color=kwargs.get("text_color", "black"),
                gate_alpha=kwargs.get("gate_alpha", 1),
            )
        else:  # single qubit setbits
            draw_single_qubit_gate(
                seq,
                setgate,
                ax,
                qubits,
                num_qubits,
                i,
                backend=None,
                greek_symbol=True,
                basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                text_color=kwargs.get("text_color", "black"),
                gate_alpha=kwargs.get("gate_alpha", 1),
            )


def plot_setqubits(
    seq: Sequence,
    gate: QuantumOperation,
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    backend: Simulator = None,
    **kwargs,
):
    """
    Plot a SetQubits operation onto a Matplotlib axis.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        gate (QuantumOperation): The target SetQubits gate instance, whose name is used to query the assigned values from the backend.
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the SetQubits operation should be placed.
        backend (Simulator, optional): Backend used to resolve symbolic or numeric parameter values. Defaults to `None`.
        **kwargs: Additional keyword arguments for styling (e.g., 'setbits_facecolor', 'setbits_edgecolor').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the SetQubits operation rendered.
    """
    name = gate.name
    if backend is not None:
        try:
            bits = backend.values[name]
            for index, bit in enumerate(bits):
                ax.add_patch(
                    FancyBboxPatch(
                        (i + 1, (num_qubits - 1 - qubits[index]) - 0.3),
                        0.6,
                        0.6,
                        boxstyle="round4,pad=0.05",
                        fill=True,
                        facecolor=kwargs.get("setbits_facecolor", "white"),
                        edgecolor=kwargs.get("setbits_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                ax.text(
                    i + 1 + 0.3,
                    num_qubits - 1 - qubits[index],
                    f"$\\vert{bit}\\rangle$",
                    ha="center",
                    va="center",
                    fontsize=15,
                    color=kwargs.get("text_color", "black"),
                    zorder=3,
                )

        except KeyError:
            setgate = BasicGate(name, len(qubits))
            if len(qubits) > 1:
                logger.warning(
                    "SetQubits values for '%s' are not specified in the backend", name
                )
                draw_multi_qubit_gate(
                    seq,
                    setgate,
                    ax,
                    qubits,
                    num_qubits,
                    i,
                    backend=None,
                    basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                    basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                    linethrough_ls=kwargs.get("linethrough_ls", "solid"),
                    wire_color=kwargs.get("wire_color", "black"),
                    text_color=kwargs.get("text_color", "black"),
                    gate_alpha=kwargs.get("gate_alpha", 1),
                )
            else:  # single qubit setbits
                logger.warning(
                    "SetQubits value for '%s' is not specified in the backend", name
                )
                draw_single_qubit_gate(
                    seq,
                    setgate,
                    ax,
                    qubits,
                    num_qubits,
                    i,
                    backend=None,
                    greek_symbol=True,
                    basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                    basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                    text_color=kwargs.get("text_color", "black"),
                    gate_alpha=kwargs.get("gate_alpha", 1),
                )
    else:
        setgate = BasicGate(name, len(qubits))
        if len(qubits) > 1:
            draw_multi_qubit_gate(
                seq,
                setgate,
                ax,
                qubits,
                num_qubits,
                i,
                backend=None,
                basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                linethrough_ls=kwargs.get("linethrough_ls", "solid"),
                wire_color=kwargs.get("wire_color", "black"),
                text_color=kwargs.get("text_color", "black"),
                gate_alpha=kwargs.get("gate_alpha", 1),
            )
        else:  # single qubit setbits
            draw_single_qubit_gate(
                seq,
                setgate,
                ax,
                qubits,
                num_qubits,
                i,
                backend=None,
                greek_symbol=True,
                basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
                basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
                text_color=kwargs.get("text_color", "black"),
                gate_alpha=kwargs.get("gate_alpha", 1),
            )


def plot_setdensitymatrix(
    seq: Sequence,
    name: str,
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a SetDensityMatrix operation onto a Matplotlib axis.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        name (str): The name of the density matrix.
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the SetDensityMatrix operation should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'setbits_facecolor', 'setbits_edgecolor').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the SetDensityMatrix operation rendered.

    """
    valid_name(name)
    name = r"\rho[{}]".format(name)
    setdensitymatrix = BasicGate(name, len(qubits))
    if len(qubits) > 1:
        draw_multi_qubit_gate(
            seq,
            setdensitymatrix,
            ax,
            qubits,
            num_qubits,
            i,
            backend=None,
            basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
            basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
            linethrough_ls=kwargs.get("linethrough_ls", "solid"),
            wire_color=kwargs.get("wire_color", "black"),
            text_color=kwargs.get("text_color", "black"),
            gate_alpha=kwargs.get("gate_alpha", 1),
        )
    else:  # single qubit setbits
        draw_single_qubit_gate(
            seq,
            setdensitymatrix,
            ax,
            qubits,
            num_qubits,
            i,
            backend=None,
            greek_symbol=True,
            basicgate_facecolor=kwargs.get("setbits_facecolor", "white"),
            basicgate_edgecolor=kwargs.get("setbits_edgecolor", "black"),
            text_color=kwargs.get("text_color", "black"),
            gate_alpha=kwargs.get("gate_alpha", 1),
        )


def plot_reverse(
    seq: Sequence,
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    **kwargs,
):
    """Plot a QubitReversal gate onto a Matplotlib axis.

    Args:
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the QubitReversal gate should be placed.
        **kwargs: Additional keyword arguments for styling (e.g., 'multigate_facecolor', 'text_color').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the QubitReversal gate rendered.

    """
    reverse_gate = BasicGate(r"\mathbb{R}\text{vrs}", len(qubits))
    draw_multi_qubit_gate(
        seq,
        reverse_gate,
        ax,
        qubits,
        num_qubits,
        i,
        backend=None,
        basicgate_facecolor=kwargs.get("multigate_facecolor", "white"),
        basicgate_edgecolor=kwargs.get("multigate_edgecolor", "black"),
        wire_ls=kwargs.get("wire_ls", "solid"),
        wire_color=kwargs.get("wire_color", "black"),
        text_color=kwargs.get("text_color", "black"),
        gate_alpha=kwargs.get("gate_alpha", 1),
    )


def draw_multi_ctrl_gate(
    seq: Sequence,
    gate: QuantumControl | ClassicalControl,
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    backend: Simulator = None,
    greek_symbol: bool = True,
    **kwargs,
):
    """Plot a multi-controlled quantum gate on a Matplotlib axis.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        gate (QuantumControl | ClassicalControl): The target multi-controlled gate instance.
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the multi-controlled gate should be placed.
        backend (Simulator, optional): Backend used to resolve symbolic or numeric parameter values. Defaults to `None`.
        greek_symbol (bool, optional): Whether to render gate labels using Greek letters when applicable. Defaults to `True`.
        **kwargs: Additional keyword arguments for styling (e.g., 'basicgate_facecolor', 'geqogate_edgecolor').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the multi-controlled gate rendered.

    """
    if isinstance(
        gate.qop,
        (
            DropQubits,
            Measure,
            SetBits,
            SetQubits,
            SetDensityMatrix,
            ClassicalControl,
        ),
    ):
        raise TypeError(
            "Non-unitary operations are not eligible targets for QuantumControl"
        )

    onoff = gate.onoff

    if isinstance(gate.qop, QuantumControl):
        if isinstance(gate, QuantumControl):
            target_gate = gate.qop.qop
            onoff1 = gate.qop.onoff
            onoff2 = onoff + onoff1
            new_op = QuantumControl(onoff2, target_gate)
            draw_multi_ctrl_gate(
                seq,
                new_op,
                ax,
                qubits,
                num_qubits,
                i,
                backend,
                greek_symbol,
                **kwargs,
            )
        else:  # Classically controlled QuantumControl
            target_gate = gate.qop.qop
            # onoff1 = gate.qop.onoff
            # new_op = QuantumControl(onoff1,target_gate)
            draw_multi_ctrl_gate(
                seq,
                gate.qop,
                ax,
                qubits[-gate.qop.getNumberQubits() :],
                num_qubits,
                i,
                backend,
                greek_symbol,
                **kwargs,
            )

            controls = qubits[: -gate.qop.getNumberQubits()]
            targets = qubits[-gate.qop.getNumberQubits() :]
            top = num_qubits - 1 - min(qubits)
            bottom = num_qubits - 1 - max(qubits)

            # enclosed box
            height_shift = (
                0.5 if set(targets) & set([min(qubits), max(qubits)]) else 0.1
            )
            width_shift = (
                0.1
                if isinstance(
                    target_gate,
                    (
                        Gates.Rzz,
                        Gates.InverseRzz,
                        Algorithms.PCCM,
                        Algorithms.InversePCCM,
                    ),
                )
                else 0
            )
            ax.add_patch(
                FancyBboxPatch(
                    (i + 1 - 0.05, bottom - height_shift / 2),
                    0.7 + width_shift,
                    top - bottom + height_shift,
                    boxstyle="round4,pad=0.05",
                    fill=False,
                    linestyle="--",
                    edgecolor=kwargs.get("wire_color", "black"),
                    alpha=kwargs.get("gate_alpha", 1),
                    zorder=2,
                )
            )
            # controlled dots
            yshift = 0
            target_gate_qubits = qubits[-target_gate.getNumberQubits() :]
            quantum_control_qubits = qubits[len(onoff) : -target_gate.getNumberQubits()]
            for index, bit in enumerate(controls):
                if (
                    bit in quantum_control_qubits
                    and bit == (min(target_gate_qubits) + max(target_gate_qubits)) / 2
                ):  # if quantum and classical control dots overlap at the middle of the target gate.
                    yshift = 0.15
                ax.add_patch(
                    plt.Circle(
                        (
                            i + 1 + 0.7 + width_shift,
                            num_qubits - 1 - bit + yshift,
                        ),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=3,
                    )
                )
                text = onoff[index]
                text_shift = 0 if text else 0.01
                ax.text(
                    i + 1 + 0.7 + width_shift - text_shift,
                    num_qubits - 1 - bit + yshift,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

    if isinstance(gate.qop, (Gates.CNOT, Gates.Toffoli)):
        if isinstance(gate, QuantumControl):
            onoff2 = list(onoff) + [1] * (gate.qop.getNumberQubits() - 1)
            plot_multix("quantum", ax, qubits, onoff2, num_qubits, i, **kwargs)
            # raise TypeError(
            # "CNOT and Toffoli are not eligible targets for QuantumControl. Please define a mulit-controlled X gate instead."
            # )
        else:  # ClassicalControl
            controls = qubits[: -gate.qop.getNumberQubits()]
            targets = qubits[-gate.qop.getNumberQubits() :]
            if isinstance(gate.qop, Gates.Toffoli):
                plot_toffoli(ax, targets, num_qubits, i, **kwargs)
            else:
                plot_cnot(ax, targets, num_qubits, i, **kwargs)

            top = num_qubits - 1 - min(qubits)
            bottom = num_qubits - 1 - max(qubits)

            # enclosed box
            height_shift = 0.5 if targets[-1] in [min(qubits), max(qubits)] else 0.1
            ax.add_patch(
                FancyBboxPatch(
                    (i + 1 - 0.05, bottom - height_shift / 2),
                    0.5,
                    top - bottom + height_shift,
                    boxstyle="round4,pad=0.05",
                    fill=False,
                    linestyle="--",
                    edgecolor=kwargs.get("wire_color", "black"),
                    alpha=kwargs.get("gate_alpha", 1),
                    zorder=2,
                )
            )
            # controlled dots
            for index, bit in enumerate(controls):
                ax.add_patch(
                    plt.Circle(
                        (i + 1 + 0.5, num_qubits - 1 - bit),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=3,
                    )
                )
                text = onoff[index]
                text_shift = 0 if text else 0.01
                ax.text(
                    i + 1 + 0.5 - text_shift,
                    num_qubits - 1 - bit,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

    if isinstance(gate.qop, (BasicGate, InverseBasicGate, Sequence)):
        name = gate.qop.name
        num_targets = gate.qop.getNumberQubits()
        facecolor = kwargs.get("basicgate_facecolor", "white")
        edgecolor = kwargs.get("basicgate_edgecolor", "black")
        valid_name(name)
        name = f"${name}$"
    else:
        if isinstance(gate.qop, Gates.PauliX):  # multi-controlled X gate
            name = None
            ctrl_type = "quantum" if isinstance(gate, QuantumControl) else "classical"
            plot_multix(ctrl_type, ax, qubits, onoff, num_qubits, i, **kwargs)
        elif isinstance(gate.qop, Gates.SwapQubits):  # controlled-swap
            name = None
            ctrl_type = "quantum" if isinstance(gate, QuantumControl) else "classical"
            plot_ctrl_swap(ctrl_type, ax, qubits, onoff, num_qubits, i, **kwargs)
        else:
            name = get_gate_name(gate.qop, backend, greek_symbol)

        num_targets = gate.qop.getNumberQubits()
        if num_targets == 1:
            facecolor = kwargs.get("geqogate_facecolor", "white")
            edgecolor = kwargs.get("geqogate_edgecolor", "black")
        else:
            facecolor = kwargs.get("multigate_facecolor", "white")
            edgecolor = kwargs.get("multigate_edgecolor", "black")

    if not isinstance(
        gate.qop,
        (
            Gates.PauliX,
            Gates.SwapQubits,
            Gates.CNOT,
            Gates.Toffoli,
            QuantumControl,
        ),
    ):
        # Sort qubits and split into controls/targets
        order = sorted(qubits)
        controls = qubits[:-num_targets]
        targets = qubits[-num_targets:]

        # Set target labels for PermuteQubits gate
        if isinstance(gate.qop, PermuteQubits):
            perm = gate.qop.targetOrder
            permq_label = {}
            for j in range(len(perm)):
                permq_label[targets[perm[j]]] = f"${seq.qubits[targets[j]]}$"

        # Control qubits within the target gate
        ctrl_in_target = set(
            order[order.index(min(targets)) : order.index(max(targets)) + 1]
        ) & set(controls)
        ctrl_in_target = list(ctrl_in_target)

        # If the target is a single qubit gate and the control type is ClassicalControl
        if num_targets == 1 and targets[0] in controls:
            if isinstance(gate, ClassicalControl):
                ctrl_in_target = [
                    targets[0]
                ]  # control bit might overlap the target qubit
            else:  # QuantumControl
                logger.error(
                    "qubit '%s' cannot be control and target qubits simultaneously.",
                    targets[0],
                )

        x_offset = (
            i + 1 + 0.35
            if isinstance(
                gate.qop,
                (
                    Algorithms.PCCM,
                    Algorithms.InversePCCM,
                    Gates.Rzz,
                    Gates.InverseRzz,
                ),
            )
            else i + 1 + 0.3
        )

        def draw_control(bit, is_on):
            """Draws a control dot for the qubit."""
            if isinstance(gate, QuantumControl):
                ax.plot(
                    x_offset,
                    num_qubits - 1 - bit,
                    marker="o",
                    markersize=6,
                    markerfacecolor="black" if is_on else "white",
                    markeredgecolor=kwargs.get("wire_color", "black"),
                )
            else:  # ClassicalControl
                ax.add_patch(
                    plt.Circle(
                        (x_offset, num_qubits - 1 - bit),
                        0.08,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                text = 1 if is_on else 0
                text_shift = 0 if is_on else 0.01
                ax.text(
                    x_offset - text_shift,
                    num_qubits - 1 - bit,
                    text,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=kwargs.get("text_color", "black"),
                    zorder=3,
                )

        def draw_vertical_line(bit1, bit2):
            """Draws a vertical line between two qubits."""
            ax.plot(
                [x_offset, x_offset],
                [num_qubits - 1 - bit1, num_qubits - 1 - bit2],
                kwargs.get("wire_color", "black"),
                lw=1,
                zorder=1,
            )

        for idx, bit in enumerate(order):
            if bit in controls:  # Controlled qubits
                if bit < min(targets):
                    draw_vertical_line(order[idx], order[idx + 1])
                    logger.info(
                        "%s has onoff %s and controls %s and bit %s",
                        gate.qop,
                        onoff,
                        controls,
                        bit,
                    )
                    draw_control(bit, onoff[controls.index(bit)])
                elif bit > max(targets):
                    draw_vertical_line(order[idx], order[idx - 1])
                    draw_control(bit, onoff[controls.index(bit)])

                elif (
                    bit in ctrl_in_target
                ):  # if controlled qubits are within the target gate
                    xoffset = (
                        0 if bit != (min(targets) + max(targets)) / 2 else 0.1
                    )  # the control dot might overlap with the text
                    if isinstance(
                        gate.qop,
                        (
                            Algorithms.PCCM,
                            Algorithms.InversePCCM,
                            Gates.Rzz,
                            Gates.InverseRzz,
                        ),
                    ):
                        xoffset += 0.1  # the width for pccm is 0.7

                    xpos = (
                        i + 1 + 0.35
                        if isinstance(
                            gate.qop,
                            (
                                Algorithms.PCCM,
                                Algorithms.InversePCCM,
                                Gates.Rzz,
                                Gates.InverseRzz,
                            ),
                        )
                        else i + 1 + 0.3
                    )

                    if bit == ctrl_in_target[0]:  # only draw once
                        if min(ctrl_in_target) != min(controls):
                            ax.plot(
                                [xpos, i + 1 + 0.55 + xoffset],
                                [
                                    num_qubits - 1 - min(targets),
                                    num_qubits - 1 - min(ctrl_in_target),
                                ],
                                kwargs.get("wire_color", "black"),
                                lw=1,
                                zorder=1,
                            )  # line beneath the gate
                        if max(ctrl_in_target) != max(controls):
                            ax.plot(
                                [xpos, i + 1 + 0.55 + xoffset],
                                [
                                    num_qubits - 1 - max(targets),
                                    num_qubits - 1 - max(ctrl_in_target),
                                ],
                                kwargs.get("wire_color", "black"),
                                lw=1,
                                zorder=1,
                            )  # line beneath the gate

                    is_on = onoff[controls.index(bit)]

                    if isinstance(
                        gate.qop,
                        (
                            Algorithms.PCCM,
                            Algorithms.InversePCCM,
                            Gates.Rzz,
                            Gates.InverseRzz,
                        ),
                    ):
                        trial_name = (
                            gate.qop.pccm.name
                            if isinstance(gate.qop, Algorithms.InversePCCM)
                            else gate.qop.name
                        )
                        if backend is not None:
                            try:
                                backend.values[trial_name]
                                markersize = 6
                            except KeyError:
                                markersize = (
                                    4 if bit == (min(targets) + max(targets)) / 2 else 6
                                )
                        else:
                            markersize = (
                                4 if bit == (min(targets) + max(targets)) / 2 else 6
                            )
                    else:
                        markersize = 6
                    if isinstance(gate, QuantumControl):
                        ax.plot(
                            i + 1 + 0.55 + xoffset,
                            num_qubits - 1 - bit,
                            marker="o",
                            markersize=markersize,
                            markerfacecolor="black" if is_on else "white",
                            markeredgecolor=kwargs.get("wire_color", "black"),
                            zorder=4,
                        )  # Control dot
                    else:  # Control dot for ClassicalControl
                        radius = (
                            0.05
                            if isinstance(gate.qop, Algorithms.InversePCCM)
                            else 0.06
                        )
                        ax.add_patch(
                            plt.Circle(
                                (i + 1 + 0.55 + xoffset, num_qubits - 1 - bit),
                                radius,
                                fill=True,
                                facecolor=kwargs.get("measure_facecolor", "white"),
                                edgecolor=kwargs.get("measure_edgecolor", "black"),
                                alpha=kwargs.get("gate_alpha", 1),
                                zorder=4,
                            )
                        )
                        text = onoff[controls.index(bit)]
                        textshift = 0.001 if text == 0 else 0
                        fontsize = (
                            5
                            if isinstance(gate.qop, Algorithms.InversePCCM)
                            and bit == (min(targets) + max(targets)) / 2
                            else 6
                        )
                        textcenter = (
                            i + 1 + 0.55 + xoffset - textshift
                            if isinstance(gate.qop, Algorithms.InversePCCM)
                            and bit == (min(targets) + max(targets)) / 2
                            else i + 1 + 0.55 + xoffset - 0.003
                        )
                        ax.text(
                            textcenter,
                            num_qubits - 1 - bit,
                            text,
                            ha="center",
                            va="center",
                            fontsize=fontsize,
                            color=kwargs.get("text_color", "black"),
                            zorder=5,
                        )

                    if (
                        bit not in targets
                    ):  # for classicalcontrol, the control bit might coincide with the targe qubits
                        ax.plot(
                            [i + 1, i + 1 + 0.55 + xoffset],
                            [num_qubits - 1 - bit, num_qubits - 1 - bit],
                            kwargs.get("wire_color", "black"),
                            ls=kwargs.get("linethrough_ls", "dashed"),
                            lw=1,
                            zorder=3,
                        )  # the control qubit wires go above the gate

            if bit == max(targets):  # Last target qubit
                height = 0.4 + max(targets) - min(targets) if len(targets) > 1 else 0.6
                width = (
                    0.7
                    if isinstance(
                        gate.qop,
                        (
                            Algorithms.PCCM,
                            Algorithms.InversePCCM,
                            Gates.Rzz,
                            Gates.InverseRzz,
                        ),
                    )
                    else 0.6
                )
                fontsize = (
                    10
                    if isinstance(
                        gate.qop,
                        (
                            Algorithms.PCCM,
                            Algorithms.InversePCCM,
                            Gates.Rzz,
                            Gates.InverseRzz,
                        ),
                    )
                    else 12
                )
                yoffset = 0.2 if len(targets) > 1 else 0.3
                ax.add_patch(
                    FancyBboxPatch(
                        (i + 1, (num_qubits - 1 - bit) - yoffset),
                        width,
                        height,
                        boxstyle="round4,pad=0.05",
                        fill=True,
                        facecolor=facecolor,
                        edgecolor=edgecolor,
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                ax.text(
                    x_offset,
                    num_qubits - 1 - (max(targets) + min(targets)) / 2,
                    name,
                    ha="center",
                    va="center",
                    fontsize=fontsize,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

                if len(targets) > 1:  # label target order on the gate
                    for qb_pos, qb in enumerate(targets):
                        offset = (
                            0 if qb != (min(targets) + max(targets)) / 2 else 0.2
                        )  # The target label might overlap the text
                        text = (
                            permq_label[qb]
                            if isinstance(gate.qop, PermuteQubits)
                            else qb_pos
                        )
                        fontsize = 8 if isinstance(gate.qop, PermuteQubits) else 10
                        ax.text(
                            i + 1.05,
                            num_qubits - qb - 1 - offset,
                            text,
                            ha="center",
                            va="center",
                            fontsize=fontsize,
                            color=kwargs.get("text_color", "black"),
                        )

        # connect control bits inside the gate
        ctrl_in_target.sort()
        xpos = [
            i + 1 + 0.55 if bit != (min(targets) + max(targets)) / 2 else i + 1 + 0.65
            for bit in ctrl_in_target
        ]
        if isinstance(
            gate.qop,
            (
                Algorithms.PCCM,
                Algorithms.InversePCCM,
                Gates.Rzz,
                Gates.InverseRzz,
            ),
        ):
            xpos = [x + 0.1 for x in xpos]  # the width for pccm is 0.7
        for idx, bit in enumerate(ctrl_in_target[:-1]):
            ax.plot(
                [xpos[idx], xpos[idx + 1]],
                [
                    num_qubits - 1 - bit,
                    num_qubits - 1 - ctrl_in_target[idx + 1],
                ],
                kwargs.get("wire_color", "black"),
                lw=1,
                zorder=3,
            )  # connecting line


def draw_multi_qubit_gate(
    seq: Sequence,
    gate: QuantumOperation,
    ax: matplotlib.axes,
    qubits: list,
    num_qubits: int,
    i: int,
    backend: Simulator = None,
    greek_symbol: bool = True,
    measure_bit: list | None = None,
    **kwargs,
):
    """Plot a multi-qubit quantum gate on a Matplotlib axis.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        gate (QuantumOperation): The target multi-qubit gate instance.
        ax (matplotlib.axes): The Matplotlib axis to draw on.
        qubits (list): A list containing the indices of the target qubits.
        num_qubits (int): Total number of qubits in the circuit.
        i (int): Column index in the circuit layout where the multi-qubit gate should be placed.
        backend (Simulator, optional): Backend used to resolve symbolic or numeric parameter values. Defaults to `None`.
        greek_symbol (bool, optional): Whether to render gate labels using Greek letters when applicable. Defaults to `True`.
        measure_bit (list, optional): A list of classical bits where the measurement results are stored. Defaults to `None`.
        **kwargs: Additional keyword arguments for styling (e.g., 'wire_color', 'linethrough_ls').

    Returns:
        matplotlib.axes: The updated Matplotlib axis with the multi-qubit gate rendered.

    """
    if isinstance(
        gate, (BasicGate, InverseBasicGate, Sequence)
    ):  # self-defined multi-qubit gate
        ax.add_patch(
            FancyBboxPatch(
                (i + 1, (num_qubits - 1 - max(qubits)) - 0.2),
                0.6,
                0.4 + (max(qubits) - min(qubits)),
                boxstyle="round4,pad=0.05",
                fill=True,
                facecolor=kwargs.get("basicgate_facecolor", "white"),
                edgecolor=kwargs.get("basicgate_edgecolor", "black"),
                alpha=kwargs.get("gate_alpha", 1),
                zorder=2,
            )
        )
        valid_name(gate.name)
        name = "${}$".format(gate.name)
        ax.text(
            i + 1 + 0.3,
            num_qubits - 1 - (max(qubits) + min(qubits)) / 2,
            name,
            ha="center",
            va="center",
            fontsize=12,
            color=kwargs.get("text_color", "black"),
            zorder=4,
        )

        for qb_pos, qb in enumerate(qubits):  # label target bits
            yoffset = 0 if qb != (min(qubits) + max(qubits)) / 2 else 0.2
            ax.text(
                i + 1.05,
                num_qubits - qb - 1 - yoffset,
                qb_pos,
                ha="center",
                va="center",
                fontsize=10,
                color=kwargs.get("text_color", "black"),
                zorder=4,
            )

        for qb in list(range(min(qubits), max(qubits) + 1)):
            if qb not in qubits:  # non-target qubits within the gate
                ax.plot(
                    [i + 1, i + 1 + 0.6],
                    [num_qubits - 1 - qb, num_qubits - 1 - qb],
                    kwargs.get("wire_color", "black"),
                    ls=kwargs.get("linethrough_ls", "dashed"),
                    lw=1,
                    zorder=3,
                )  # the wire goes above the gate

    if isinstance(gate, QuantumOperation) and not isinstance(
        gate, (QuantumControl, ClassicalControl)
    ):  # geqo multi-qubit gates
        name = get_gate_name(gate, backend, greek_symbol)

        if name is None:
            if isinstance(gate, Gates.CNOT):
                plot_cnot(ax=ax, qubits=qubits, num_qubits=num_qubits, i=i, **kwargs)
            if isinstance(gate, Gates.Toffoli):
                plot_toffoli(ax=ax, qubits=qubits, num_qubits=num_qubits, i=i, **kwargs)
            if isinstance(gate, Gates.SwapQubits):
                plot_swap(ax=ax, qubits=qubits, num_qubits=num_qubits, i=i, **kwargs)
            if isinstance(gate, DropQubits):
                plot_dropbits(
                    ax=ax, qubits=qubits, num_qubits=num_qubits, i=i, **kwargs
                )
            if isinstance(gate, SetBits):
                plot_setbits(
                    seq=seq,
                    gate=gate,
                    ax=ax,
                    qubits=qubits,
                    num_qubits=num_qubits,
                    i=i,
                    backend=backend,
                    **kwargs,
                )
            if isinstance(gate, SetQubits):
                plot_setqubits(
                    seq=seq,
                    gate=gate,
                    ax=ax,
                    qubits=qubits,
                    num_qubits=num_qubits,
                    i=i,
                    backend=backend,
                    **kwargs,
                )
            if isinstance(gate, SetDensityMatrix):
                plot_setdensitymatrix(
                    seq=seq,
                    name=gate.name,
                    ax=ax,
                    qubits=qubits,
                    num_qubits=num_qubits,
                    i=i,
                    **kwargs,
                )

        elif isinstance(gate, QubitReversal):
            plot_reverse(
                seq=seq,
                ax=ax,
                qubits=qubits,
                num_qubits=num_qubits,
                i=i,
                **kwargs,
            )

        elif isinstance(gate, Measure):  # multi-qubit Measure
            for idx, qb in enumerate(qubits):
                ax.add_patch(
                    plt.Circle(
                        (i + 1 + 0.2, num_qubits - 1 - qb),
                        0.2,
                        fill=True,
                        facecolor=kwargs.get("measure_facecolor", "white"),
                        edgecolor=kwargs.get("measure_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                ax.text(
                    i + 1 + 0.2,
                    num_qubits - 1 - qb,
                    name,
                    ha="center",
                    va="center",
                    fontsize=15,
                    color=kwargs.get("text_color", "black"),
                )
                # if measure_bit is None:
                # measure_bit = qubits
                ax.text(
                    i + 1 + 0.45,
                    num_qubits - 1 - qb - 0.25,
                    measure_bit[idx],
                    ha="center",
                    va="center",
                    fontsize=10,
                    color=kwargs.get("wire_color", "black"),
                )
        else:
            if isinstance(
                gate,
                (
                    Algorithms.PCCM,
                    Algorithms.InversePCCM,
                    Gates.Rzz,
                    Gates.InverseRzz,
                ),
            ):
                ax.add_patch(
                    FancyBboxPatch(
                        (i + 1, (num_qubits - 1 - max(qubits)) - 0.2),
                        0.7,
                        0.4 + (max(qubits) - min(qubits)),
                        boxstyle="round4,pad=0.05",
                        fill=True,
                        facecolor=kwargs.get("multigate_facecolor", "white"),
                        edgecolor=kwargs.get("multigate_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                ax.text(
                    i + 1 + 0.35,
                    num_qubits - 1 - (max(qubits) + min(qubits)) / 2,
                    name,
                    ha="center",
                    va="center",
                    fontsize=10,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )
            else:
                ax.add_patch(
                    FancyBboxPatch(
                        (i + 1, (num_qubits - 1 - max(qubits)) - 0.2),
                        0.6,
                        0.4 + (max(qubits) - min(qubits)),
                        boxstyle="round4,pad=0.05",
                        fill=True,
                        facecolor=kwargs.get("multigate_facecolor", "white"),
                        edgecolor=kwargs.get("multigate_edgecolor", "black"),
                        alpha=kwargs.get("gate_alpha", 1),
                        zorder=2,
                    )
                )
                ax.text(
                    i + 1 + 0.3,
                    num_qubits - 1 - (max(qubits) + min(qubits)) / 2,
                    name,
                    ha="center",
                    va="center",
                    fontsize=12,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

            if isinstance(gate, PermuteQubits):
                perm = gate.targetOrder
                permq_label = {}
                for j in range(len(perm)):
                    permq_label[qubits[perm[j]]] = f"${seq.qubits[qubits[j]]}$"

            for qb_pos, qb in enumerate(qubits):
                yoffset = 0 if qb != (min(qubits) + max(qubits)) / 2 else 0.2
                # Set target labels for PermuteQubits gate
                text = permq_label[qb] if isinstance(gate, PermuteQubits) else qb_pos
                fontsize = 8 if isinstance(gate, PermuteQubits) else 10
                ax.text(
                    i + 1.05,
                    num_qubits - qb - 1 - yoffset,
                    text,
                    ha="center",
                    va="center",
                    fontsize=fontsize,
                    color=kwargs.get("text_color", "black"),
                    zorder=4,
                )

            for qb in list(range(min(qubits), max(qubits) + 1)):
                if qb not in qubits:  # non-target qubit within the gate (linethrough)
                    if isinstance(
                        gate,
                        (
                            Algorithms.PCCM,
                            Algorithms.InversePCCM,
                            Gates.Rzz,
                            Gates.InverseRzz,
                        ),
                    ):
                        ax.plot(
                            [i + 1, i + 1 + 0.7],
                            [num_qubits - 1 - qb, num_qubits - 1 - qb],
                            kwargs.get("wire_color", "black"),
                            ls=kwargs.get("linethrough_ls", "dashed"),
                            lw=1,
                            zorder=3,
                        )
                    else:
                        ax.plot(
                            [i + 1, i + 1 + 0.6],
                            [num_qubits - 1 - qb, num_qubits - 1 - qb],
                            kwargs.get("wire_color", "black"),
                            ls=kwargs.get("linethrough_ls", "dashed"),
                            lw=1,
                            zorder=3,
                        )


def plot_mpl(
    seq: Sequence,
    backend: Simulator = None,
    decompose_subseq: bool = False,
    pack: bool = True,
    fold: int = 25,
    style: str = None,
    greek_symbol: bool = True,
    filename: str = None,
    **kwargs,
):
    """Plot a matplotlib-style quantum circuit diagram from a geqo `Sequence`.

    Args:
        seq (Sequence): The geqo `Sequence` to visualize.
        backend (Simulator, optional): The simulator backend used to resolve parameter values. Defaults to `None`.
        decompose_subseq (bool, optional): Whether to decompose subsequences within the main sequence. Defaults to `False`.
        pack (bool, optional): Whether to compactify the circuit by placing non-conflicting gates in the same column. Defaults to `True`.
        fold (int, optional): Maximum number of columns to show before folding the circuit. Defaults to 25.
        style (str, optional): Predefined plot style to be applied. Defaults to `None` (black and white theme).
        greek_symbol (bool, optional): Whether to render gate names using Greek letters. Defaults to `True`.
        filename (str, optional): If provided, the output PNG will be saved with this filename. Defaults to `None`.
        **kwargs: Additional styling options passed to the matplotlib-style circuit generator.

    Returns:
        matplotlib.figure.Figure: The matplotlib-style quantum circuit diagram.

    """
    num_qubits = len(seq.qubits)
    if decompose_subseq:
        seq = embedSequences(seq)
    tem_operations = seq.gatesAndTargets

    operations = []
    for op in tem_operations:
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
                target if type(target) is int else seq.bits.index(target)
                for target in op[2]
            ]
            operations.append((op[0], int_targets, int_ctargets))

    predefined_styles = {
        "geqo": {
            "fig_facecolor": "bisque",
            "ax_facecolor": "bisque",
            "wire_color": "gray",
            "wire_ls": "dashdot",
            "linethrough_ls": "dashdot",
            "gate_alpha": 0.85,
            "geqogate_facecolor": "lightskyblue",
            "geqogate_edgecolor": "deepskyblue",
            "basicgate_facecolor": "springgreen",
            "basicgate_edgecolor": "limegreen",
            "drop_color": "dimgray",
            "setbits_facecolor": "violet",
            "setbits_edgecolor": "plum",
            "multigate_facecolor": "gold",
            "multigate_edgecolor": "goldenrod",
            "measure_facecolor": "salmon",
            "measure_edgecolor": "tomato",
        },
        "geqo_dark": {
            "fig_facecolor": "black",
            "ax_facecolor": "black",
            "wire_color": "white",
            "wire_ls": "dashdot",
            "linethrough_ls": "dashdot",
            "gate_alpha": 0.85,
            "geqogate_facecolor": "lightskyblue",
            "geqogate_edgecolor": "deepskyblue",
            "basicgate_facecolor": "springgreen",
            "basicgate_edgecolor": "limegreen",
            "drop_color": "dimgray",
            "setbits_facecolor": "violet",
            "setbits_edgecolor": "plum",
            "multigate_facecolor": "gold",
            "multigate_edgecolor": "goldenrod",
            "measure_facecolor": "salmon",
            "measure_edgecolor": "tomato",
        },
        "jos": {
            "text_color": "white",
            "gate_alpha": 0.85,
            "linethrough_ls": "dashed",
            "geqogate_facecolor": "#8418DC",
            "geqogate_edgecolor": "#570D93",
            "basicgate_facecolor": "#1A01DC",
            "basicgate_edgecolor": "#100193",
            "drop_color": "dimgray",
            "setbits_facecolor": "violet",
            "setbits_edgecolor": "plum",
            "multigate_facecolor": "#4CA7A5",
            "multigate_edgecolor": "#316E6D",
            "measure_facecolor": "salmon",
            "measure_edgecolor": "tomato",
        },
        "jos_dark": {
            "fig_facecolor": "black",
            "ax_facecolor": "black",
            "wire_color": "white",
            "text_color": "white",
            "gate_alpha": 0.85,
            "linethrough_ls": "dashed",
            "geqogate_facecolor": "#8418DC",
            "geqogate_edgecolor": "#570D93",
            "basicgate_facecolor": "#1A01DC",
            "basicgate_edgecolor": "#100193",
            "drop_color": "dimgray",
            "setbits_facecolor": "violet",
            "setbits_edgecolor": "plum",
            "multigate_facecolor": "#4CA7A5",
            "multigate_edgecolor": "#316E6D",
            "measure_facecolor": "salmon",
            "measure_edgecolor": "tomato",
        },
        "dark": {
            "fig_facecolor": "black",
            "ax_facecolor": "black",
            "wire_color": "white",
            "linethrough_ls": "dashed",
            "text_color": "white",
            "geqogate_facecolor": "black",
            "geqogate_edgecolor": "white",
            "drop_color": "white",
            "basicgate_facecolor": "black",
            "basicgate_edgecolor": "white",
            "setbits_facecolor": "black",
            "setbits_edgecolor": "white",
            "multigate_facecolor": "black",
            "multigate_edgecolor": "white",
            "measure_facecolor": "black",
            "measure_edgecolor": "white",
        },
    }

    style_settings = predefined_styles.get(
        style, {}
    )  # Get selected style or empty dict
    kwargs = {
        **style_settings,
        **kwargs,
    }  # Merge style settings with custom kwargs

    if pack:
        operations = pack_gates(operations)

    fold = max(1, min(fold, 33))  # Ensure fold is within [1, 33]
    ax_rows = -(
        -len(operations) // fold
    )  # Equivalent to math.ceil(len(operations) / fold)
    plot_width = min(len(operations), fold)
    fig, axes = plt.subplots(nrows=ax_rows, figsize=(plot_width, num_qubits * ax_rows))
    ax = [axes] if ax_rows == 1 else axes  # Ensure axes is always a list

    fig.patch.set_facecolor(kwargs.get("fig_facecolor", "white"))

    for i_row in range(ax_rows):
        ax[i_row].set_facecolor(kwargs.get("ax_facecolor", "white"))
        ax[i_row].set_xlim(0, plot_width + 1)
        ax[i_row].set_ylim(-0.5, num_qubits - 0.5)

        # Draw qubit wires first
        for i in range(num_qubits):
            ax[i_row].plot(
                [0, fold + 0.5],
                [i, i],
                kwargs.get("wire_color", "black"),
                lw=kwargs.get("wire_lw", 1),
                ls=kwargs.get("wire_ls", "solid"),
                zorder=1,
            )
            # ax[i_row].text(-0.2, num_qubits-1-i, f"$q_{i}$", ha="center", va="center", color = kwargs.get("wire_color", "black"), fontsize=12, zorder=2)
            ax[i_row].text(
                -0.2,
                num_qubits - 1 - i,
                f"${seq.qubits[i]}$",
                ha="center",
                va="center",
                color=kwargs.get("wire_color", "black"),
                fontsize=12,
                zorder=2,
            )

        start, end = fold * i_row, min(fold * (i_row + 1), len(operations))
        for i_col, column in enumerate(operations[start:end]):
            if not isinstance(column, list):
                column = [column]
            for operation in column:
                gate = operation[0]
                qubits = operation[1]
                if isinstance(gate, Measure):
                    measure_bit = operation[2]
                else:
                    measure_bit = None
                if len(qubits) == 1:
                    draw_single_qubit_gate(
                        seq=seq,
                        gate=gate,
                        ax=ax[i_row],
                        num_qubits=num_qubits,
                        qubits=qubits,
                        i=i_col,
                        backend=backend,
                        greek_symbol=greek_symbol,
                        measure_bit=measure_bit,
                        **kwargs,
                    )
                elif isinstance(gate, (QuantumControl, ClassicalControl)):
                    draw_multi_ctrl_gate(
                        seq=seq,
                        gate=gate,
                        ax=ax[i_row],
                        num_qubits=num_qubits,
                        qubits=qubits,
                        i=i_col,
                        backend=backend,
                        greek_symbol=greek_symbol,
                        **kwargs,
                    )
                else:
                    draw_multi_qubit_gate(
                        seq=seq,
                        gate=gate,
                        ax=ax[i_row],
                        num_qubits=num_qubits,
                        qubits=qubits,
                        i=i_col,
                        backend=backend,
                        greek_symbol=greek_symbol,
                        measure_bit=measure_bit,
                        **kwargs,
                    )
                """draw_func = (
                    draw_single_qubit_gate
                    if len(qubits) == 1
                    else draw_multi_ctrl_gate
                    if isinstance(gate, (QuantumControl, ClassicalControl))
                    else draw_multi_qubit_gate
                )
                draw_func(
                    seq=seq,
                    gate=gate,
                    ax=ax[i_row],
                    num_qubits=num_qubits,
                    qubits=qubits,
                    i=i_col,
                    backend=backend,
                    greek_symbol=greek_symbol,
                    **kwargs,
                )"""

        ax[i_row].axis("off")
        ax[i_row].set_aspect(1.0)  # could be problematic
    plt.tight_layout()

    if filename is not None:
        fig.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")


#########################################################
########### histograms of measurement results ###########
#########################################################


def plot_hist(
    ensemble: dict,
    style: str = "geqo",
    show_bar_labels: bool = False,
    intermediate_bins: int = 10,
    filename: str = None,
    **kwargs,
):
    """Plot histograms of the measurement results.

    Args:
        ensemble (dict): The dictionary that stores the probability and density matrix of each measurement outcome.
        style (str, optional): The predefined style to use for the histograms. Defaults to `geqo`.
        show_bar_labels (bool, optional): Whether to display the numerical values on the histogram bars. Defaults to `False`.
        intermediate_bins (int, optional): The number of bins displayed in the last histogram if there are more than 64 measurement outcomes. Defaults to 10
        filename (str, optional): If provided, the output PNG will be saved with this filename. Defaults to `None`.
        **kwargs: Additional styling options passed to the plotting function.

    Returns:
        matplotlib.figure.Figure: The matplotlib Figure object containing the histogram plots.

    """
    predefined_styles = {
        "geqo": {
            "cmap": ["deepskyblue", "springgreen", "gold", "tomato"],
            "facecolor": "bisque",
            "framecolor": "silver",
            "tickscolor": "black",
            "bar_edgecolor": "silver",
            "bar_alpha": 0.95,
            "grid_alpha": 0.6,
            "occurrence_bar_color": "gold",
        },
        "geqo_dark": {
            "cmap": ["deepskyblue", "springgreen", "gold", "tomato"],
            "facecolor": "black",
            "framecolor": "silver",
            "tickscolor": "white",
            "bar_edgecolor": "silver",
            "bar_alpha": 0.95,
            "grid_alpha": 0.6,
            "occurrence_bar_color": "gold",
        },
        "jos_dark": {
            "cmap": ["#4CA7A5", "#8418DC", "#1A01DC"],
            "facecolor": "black",
            "framecolor": "silver",
            "tickscolor": "white",
            "bar_edgecolor": "black",
            "bar_alpha": 0.95,
            "grid_alpha": 0.3,
            "occurrence_bar_color": "cyan",
        },
        "jos": {
            "cmap": ["#4CA7A5", "#8418DC", "#1A01DC"],
            "facecolor": "white",
            "framecolor": "black",
            "tickscolor": "black",
            "bar_edgecolor": "black",
            "bar_alpha": 0.95,
            "grid_alpha": 0.8,
            "occurrence_bar_color": "cyan",
        },
        "dark": {
            "cmap": ["k", "dimgray", "lightgray", "white"],
            "facecolor": "black",
            "framecolor": "silver",
            "tickscolor": "white",
            "bar_edgecolor": "silver",
            "bar_alpha": 0.95,
            "grid_alpha": 0.6,
            "occurrence_bar_color": "silver",
        },
    }

    style_settings = predefined_styles.get(
        style, {}
    )  # Get selected style or empty dict
    kwargs = {
        **style_settings,
        **kwargs,
    }  # Merge style settings with custom kwargs

    # convert input data into two lists: basis_states and probs
    basis_states = []
    probs = []
    for key, item in ensemble.items():
        if key != "mixed_state":
            basis_states.append(key)
            if isinstance(item, tuple):
                probs.append(item[0])
            else:
                probs.append(item)
    basis_states = [
        "".join(str(b) for b in basis_state) for basis_state in basis_states
    ]
    probs = [float(p) for p in probs]  # turn sympy float objects into python floats

    # define bar colors
    cmap1D = matplotlib.colors.LinearSegmentedColormap.from_list(
        "", kwargs.get("cmap", ["white", "grey", "black"])
    )
    norm = plt.Normalize(
        vmin=min(probs), vmax=max(probs)
    )  # Normalize the data for colormap
    colors = [cmap1D(float(norm(value))) for value in probs]

    def plot_bar(figsize):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor(kwargs.get("facecolor", "white"))
        ax.set_facecolor(kwargs.get("facecolor", "white"))
        ax.tick_params(
            axis="x", colors=kwargs.get("tickscolor", "black")
        )  # X-axis ticks
        ax.tick_params(axis="y", colors=kwargs.get("tickscolor", "black"))
        for spine in ax.spines.values():
            spine.set_color(kwargs.get("framecolor", "black"))

        figwidth = fig.get_size_inches()[0]
        bar_width = min(figwidth / 4, figwidth / len(basis_states)) * 0.5

        bars = ax.bar(
            basis_states,
            probs,
            width=bar_width,
            edgecolor=kwargs.get("bar_edgecolor", "black"),
            color=colors,
            alpha=kwargs.get("bar_alpha", 0.95),
        )

        # 5. Customize plot
        ax.set_xticks(basis_states)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="center")
        ax.set_ylabel("Probability", color=kwargs.get("tickscolor", "black"))
        ax.set_title("Measurement Results", color=kwargs.get("tickscolor", "black"))
        ax.grid(True, linestyle="--", alpha=kwargs.get("grid_alpha", 0.6))

        if show_bar_labels:
            # add prob labels on top of bars
            for bar, prb in zip(bars, probs, strict=False):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + max(probs) * 0.1,
                    f"{prb:.1e}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    rotation=50,
                    color=kwargs.get("tickscolor", "black"),
                )

            # leave some space for prob labels
            ax.set_ylim([0, max(probs) * 1.2])

        else:  # show the prob labels if mplcursors is installed.
            try:
                import mplcursors

                # Enable interactive tooltips
                cursor = mplcursors.cursor(bars, hover=True)

                @cursor.connect("add")
                def on_hover(sel):
                    height = sel.artist[sel.index].get_height()
                    sel.annotation.set_text(f"{height:.8f}")
                    # sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

            except ImportError:
                logger.exception(
                    "mplcursors not installed. Interactive cursor is not activated"
                )
                pass

        ax.format_coord = (
            lambda x, y: ""
        )  # hide the little coordinate (x,y) shown by widget
        plt.tight_layout()

        if filename is not None:
            fig.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")

    if len(basis_states) <= 16:
        figsize = (8, 4)
        plot_bar(figsize)

    elif 16 < len(basis_states) <= 32:
        figsize = (16, 4)  # double the figure width
        plot_bar(figsize)

    else:  # too many measurement outcomes
        nrows = 3 if len(basis_states) > 64 else 2
        figsize = (16, 4 * nrows)
        fig, ax = plt.subplots(nrows, 1, figsize=figsize)
        fig.patch.set_facecolor(kwargs.get("facecolor", "white"))

        if nrows == 3:
            sorted_indices = sorted(range(len(probs)), key=lambda i: probs[i])
            top_prob = sorted(probs)[-32:]
            bot_prob = sorted(probs)[:32]
            top_basis = [basis_states[i] for i in sorted_indices[-32:]]
            bot_basis = [basis_states[i] for i in sorted_indices[:32]]
            top_color = [colors[i] for i in sorted_indices[-32:]]
            bot_color = [colors[i] for i in sorted_indices[:32]]
            mid_prob = sorted(probs)[32:-32]

        for i in range(nrows):
            ax[i].set_facecolor(kwargs.get("facecolor", "white"))
            ax[i].tick_params(
                axis="x", colors=kwargs.get("tickscolor", "black")
            )  # X-axis ticks
            ax[i].tick_params(axis="y", colors=kwargs.get("tickscolor", "black"))
            for spine in ax[i].spines.values():
                spine.set_color(kwargs.get("framecolor", "black"))

            ax[i].grid(True, linestyle="--", alpha=kwargs.get("grid_alpha", 0.6))

            if nrows == 2:
                num_bins1 = (
                    len(probs) // 2 if len(probs) % 2 == 0 else len(probs) // 2 + 1
                )
                if i == 0:
                    res_probs = probs[:num_bins1]
                    bits = basis_states[:num_bins1]
                    res_colors = colors[:num_bins1]
                    ax[i].set_title(
                        "Measurement Results",
                        color=kwargs.get("tickscolor", "black"),
                    )
                else:
                    res_probs = probs[num_bins1:]
                    bits = basis_states[num_bins1:]
                    res_colors = colors[num_bins1:]

                bar_width = 16 / len(bits) * 0.5

                bars = ax[i].bar(
                    bits,
                    res_probs,
                    width=bar_width,
                    edgecolor=kwargs.get("bar_edgecolor", "black"),
                    color=res_colors,
                    alpha=kwargs.get("bar_alpha", 0.95),
                )
                ax[i].set_xticks(bits)
                ax[i].set_xticklabels(ax[i].get_xticklabels(), rotation=45, ha="center")
                ax[i].set_ylabel("Probability", color=kwargs.get("tickscolor", "black"))

                if show_bar_labels:
                    # add prob labels on top of bars
                    for bar, prb in zip(bars, res_probs, strict=False):
                        height = bar.get_height()
                        ax[i].text(
                            bar.get_x() + bar.get_width() / 2,
                            height + max(res_probs) * 0.1,
                            f"{prb:.1e}",
                            ha="center",
                            va="center",
                            fontsize=9,
                            rotation=50,
                            color=kwargs.get("tickscolor", "black"),
                        )

                    # leave some space for prob labels
                    ax[i].set_ylim([0, max(res_probs) * 1.2])

                else:  # show the prob labels if mplcursors is installed.
                    try:
                        import mplcursors

                        # Enable interactive tooltips
                        cursor = mplcursors.cursor(bars, hover=True)

                        @cursor.connect("add")
                        def on_hover(sel):
                            height = sel.artist[sel.index].get_height()
                            sel.annotation.set_text(f"{height:.8f}")
                            # sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

                    except ImportError:
                        logger.exception(
                            "mplcursors not installed. Interactive cursor is not activated"
                        )
                        pass

            else:  # nrows=3
                if i < 2:
                    bar_width = 0.25
                    res_probs = top_prob if i == 0 else bot_prob
                    bits = top_basis if i == 0 else bot_basis
                    res_colors = top_color if i == 0 else bot_color

                    bars = ax[i].bar(
                        bits,
                        res_probs,
                        width=bar_width,
                        edgecolor=kwargs.get("bar_edgecolor", "black"),
                        color=res_colors,
                        alpha=kwargs.get("bar_alpha", 0.95),
                    )
                    ax[i].set_xticks(bits)
                    ax[i].set_xticklabels(
                        ax[i].get_xticklabels(), rotation=45, ha="center"
                    )
                    ax[i].set_ylabel(
                        "Probability", color=kwargs.get("tickscolor", "black")
                    )

                    title = (
                        "Most likely outcomes"
                        if i == 0
                        else "Least likely (non-zero) outcomes"
                    )
                    ax[i].set_title(title, color=kwargs.get("tickscolor", "black"))

                    if show_bar_labels:
                        # add prob labels on top of bars
                        for bar, prb in zip(bars, res_probs, strict=False):
                            height = bar.get_height()
                            ax[i].text(
                                bar.get_x() + bar.get_width() / 2,
                                height + max(res_probs) * 0.1,
                                f"{prb:.1e}",
                                ha="center",
                                va="center",
                                fontsize=9,
                                rotation=50,
                                color=kwargs.get("tickscolor", "black"),
                            )

                        # leave some space for prob labels
                        ax[i].set_ylim([0, max(res_probs) * 1.2])

                    else:  # show the prob labels if mplcursors is installed.
                        try:
                            import mplcursors

                            # Enable interactive tooltips
                            cursor = mplcursors.cursor(bars, hover=True)

                            @cursor.connect("add")
                            def on_hover(sel):
                                height = sel.artist[sel.index].get_height()
                                sel.annotation.set_text(f"{height:.8f}")
                                # sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

                        except ImportError:
                            logger.exception(
                                "mplcursors not installed. Interactive cursor is not activated"
                            )
                            pass

                else:  # last row (display pecrentage vs. probability interval)
                    bin_edges = np.linspace(
                        min(mid_prob), max(mid_prob), intermediate_bins + 1
                    )

                    if min(mid_prob) != max(mid_prob):
                        counts, _ = np.histogram(mid_prob, bins=bin_edges)
                        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                    else:
                        counts = [len(mid_prob)]
                        bin_centers = [mid_prob[0]]
                    # percentages = (counts / len(mid_prob)) * 100

                    bar_width = (bin_edges[1] - bin_edges[0]) * 0.5

                    if min(mid_prob) != max(mid_prob):
                        bars = ax[i].bar(
                            bin_centers,
                            counts,
                            width=bar_width,
                            edgecolor=kwargs.get("bar_edgecolor", "black"),
                            color=kwargs.get("occurrence_bar_color", "silver"),
                        )
                    else:  # if all the probailities are the same
                        bars = ax[i].bar(
                            [mid_prob[0]],
                            counts,
                            edgecolor=kwargs.get("bar_edgecolor", "black"),
                            color=kwargs.get("occurrence_bar_color", "silver"),
                        )

                    ax[i].set_xlabel(
                        "Probability interval",
                        color=kwargs.get("tickscolor", "black"),
                    )
                    # ax[i].set_ylabel('Percentage (%)',color=kwargs.get("tickscolor","black"))
                    ax[i].set_ylabel("Counts", color=kwargs.get("tickscolor", "black"))
                    ax[i].set_title(
                        "Occurrence of intermediate outcomes",
                        color=kwargs.get("tickscolor", "black"),
                    )
                    ax[i].set_xticks([float(x) for x in bin_centers])
                    # ax[i].set_xticklabels(ax[i].get_xticklabels(), rotation=45, ha='center')
                    if min(mid_prob) != max(mid_prob):
                        ax[i].set_xticklabels(
                            [
                                f"{float(bin_edges[j]):.1e}-{float(bin_edges[j + 1]):.1e}"
                                for j in range(len(bin_edges) - 1)
                            ],
                            rotation=45,
                            ha="center",
                        )
                    else:
                        ax[i].set_xticklabels(
                            [f"{float(mid_prob[0]):.1e}"],
                            rotation=45,
                            ha="center",
                        )

                    if show_bar_labels:
                        # add counts labels on top of bars
                        for bar, ct in zip(bars, counts, strict=False):
                            height = bar.get_height()
                            ax[i].text(
                                bar.get_x() + bar.get_width() / 2,
                                height + 0.5,
                                f"{ct}",
                                ha="center",
                                va="center",
                                fontsize=12,
                                color=kwargs.get("tickscolor", "black"),
                            )

                        # leave some space for counts labels
                        ax[i].set_ylim([0, max(counts) + 5])

                    else:  # show the counts labels if mplcursors is installed.
                        try:
                            import mplcursors

                            # Enable interactive tooltips
                            cursor = mplcursors.cursor(bars, hover=True)

                            @cursor.connect("add")
                            def on_hover(sel):
                                height = sel.artist[sel.index].get_height()
                                sel.annotation.set_text(f"{height:.8f}")
                                # sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

                        except ImportError:
                            logger.exception(
                                "mplcursors not installed. Interactive cursor is not activated"
                            )
                            pass
        for axis in ax:
            axis.format_coord = (
                lambda x, y: ""
            )  # hide the (x,y) annotation below the figure in widget mode
        plt.tight_layout()

        if filename is not None:
            fig.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")
