from abc import ABC, abstractmethod

import geqo.gates as gates
from geqo.__logger__ import get_logger
from geqo.algorithms.algorithms import (
    PCCM,
    QFT,
    InversePCCM,
    InverseQFT,
    PermuteQubits,
    QubitReversal,
)
from geqo.core.quantum_circuit import Sequence
from geqo.core.quantum_operation import QuantumOperation
from geqo.initialization.state import SetQubits
from geqo.operations.controls import ClassicalControl, QuantumControl
from geqo.operations.measurement import Measure
from geqo.utils._base_.helpers import embedSequences

logger = get_logger(__name__)


class Simulator(ABC):
    """The super class for all backends."""

    @abstractmethod
    def __init__(self):
        """
        The constructor of a simulator. In many cases, it takes as parameters the number of classical bits, the number of qubits
        and a list of values, which are needed to run all operations. The specific parameters might depend on the implementation.
        """
        pass

    @abstractmethod
    def __repr__(self):
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        pass

    @abstractmethod
    def apply(self):
        """
        Apply an operation to the state, which is currently kept in the simulator. Besides the operation, which is applied, in
        many cases, this method also takes as parameters the targets of the operations, which might be qubits, classical
        bits or both. The specific parameters might depend on the implementation.
        """
        pass


class BaseQASM(Simulator):
    """Base class for QASM3 code."""

    def __init__(self, values: dict):
        """
        The constructor of this simulator takes as parameters the number of classical bits, the number of qubits
        and a list of values, which are needed to run all operations.

        Parameters
        ----------
        values : {key:value}
            A dictionary of keys and values, which are needed for simulating the operations.

        Returns
        -------
        self : geqo.simulators.BaseQASM
            A simulator backend for turning quantum operations to QASM3 code.
        """
        self.values = values

    def __repr__(self) -> str:
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return (
            "QASM3 converter initialized."
            + f"Parameters queried from values dictionary: {self.values}"
        )

    def apply(self, sequence: Sequence) -> None:
        """
        Apply an object of the class ```Sequence``` to this backend.  This method does not to anything, because this class is the super-class of all implementations of QASM3 backends.
        """
        logger.info("Apply Sequence %s to QASM3 converter.", sequence)
        return None

    def permutation_swap(self, perm: list[int]) -> list[tuple[int, int]]:
        qubits = [*range(len(perm))]
        new_pos = qubits.copy()
        swap = []
        for i in range(len(perm) - 1):
            if new_pos.index(qubits[i]) != perm[i]:
                swap.append((qubits[i], new_pos[perm[i]]))
                new_pos[new_pos.index(qubits[i])] = new_pos[perm[i]]
                new_pos[perm[i]] = qubits[i]
        return swap

    def gate_to_qasm(
        self, gate: QuantumOperation | str, targets: list[int]
    ) -> str:  # fundamental single-qubit and multi-qubit gates
        """
        Turn a quantum operation to a QASM3 character string.

        Parameters
        ----------
        gate : geqo.core.quantum_operations.QuantumOperation
            The gate that should be converted to QASM.
        targets : list(int)
            The indexes of the qubits, on which the quantum operation works.

        Returns
        -------
        String
            The QASM3 code corresponding to the quantum operation.

        """
        if isinstance(gate, (QFT, InverseQFT, QubitReversal, PCCM, InversePCCM)):
            decom = gate.getEquivalentSequence()
            translated_lines = []
            for item in decom.gatesAndTargets:
                subgate, targets = item
                translated_lines.append(self.translate_gate(subgate, targets))
            return "\n".join(translated_lines)
        elif isinstance(gate, gates.PauliX):
            return f"x q[{targets[0]}];"
        elif isinstance(gate, gates.PauliY):
            return f"y q[{targets[0]}];"
        elif isinstance(gate, gates.PauliZ):
            return f"z q[{targets[0]}];"
        elif isinstance(gate, gates.Hadamard):
            return f"h q[{targets[0]}];"
        elif isinstance(gate, gates.SGate):
            return f"s q[{targets[0]}];"
        elif isinstance(gate, gates.InverseSGate):
            return f"sdg q[{targets[0]}];"
        elif isinstance(gate, gates.CNOT):
            return f"cx q[{targets[0]}], q[{targets[1]}];"
        elif isinstance(gate, gates.SwapQubits):
            return f"swap q[{targets[0]}], q[{targets[1]}];"
        elif isinstance(gate, gates.Phase):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"p({angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.InversePhase):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"p(-{angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.Rx):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"rx({angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.Ry):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"ry({angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.Rz):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"rz({angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.InverseRx):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"rx(-{angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.InverseRy):
            try:
                angle = self.values[gate.name]
            except KeyError:
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"ry(-{angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.InverseRz):
            try:
                angle = self.values[gate.name]
            except KeyError:
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"rz(-{angle}) q[{targets[0]}];"
        elif isinstance(gate, gates.Rzz):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"rzz({angle}) q[{targets[0]}], q[{targets[1]}];"
        elif isinstance(gate, gates.InverseRzz):
            try:
                angle = self.values[gate.name]
            except KeyError:
                logger.exception(
                    "Cannot fetch phase angle %s from the backend.", gate.name
                )
                raise ValueError(
                    f"Cannot fetch phase angle {gate.name} from the backend."
                )
            return f"rzz(-{angle}) q[{targets[0]}], q[{targets[1]}];"
        elif isinstance(gate, gates.Toffoli):
            return f"ccx q[{targets[0]}], q[{targets[1]}], q[{targets[2]}];"
        elif isinstance(gate, PermuteQubits):
            swaps = self.permutation_swap(gate.targetOrder)
            return "\n".join([f"swap q[{i}], q[{j}];" for i, j in swaps])
        elif isinstance(gate, SetQubits):
            try:
                qubit_values = self.values[gate.name]
                strlist = []
                for i in range(len(targets)):
                    strlist.append(f"reset q[{targets[i]}];")
                    if qubit_values[i] == 1:  # set bit to 1
                        strlist.append(f"x q[{targets[i]}];")
            except KeyError:
                logger.error(
                    "Cannot fetch SetQubits values %s from the backend.",
                    gate.name,
                )
                raise ValueError(
                    f"Cannot fetch SetQubits values {gate.name} from the backend."
                )
            return "\n".join(strlist)
        else:
            raise NotImplementedError(f"Unsupported gate/operation: {gate}")

    def translate_gate(
        self,
        gate: QuantumOperation | str,
        targets: list[int],
        bits: list[int] | None = None,
    ) -> str | None:
        # for QuantumControl, ClassicalControl and Measure
        if isinstance(gate, QuantumControl):
            onoff = gate.onoff
            ctrl_qubits = targets[: len(onoff)]
            target_qubits = targets[len(onoff) :]

            # Apply X gates to control qubits that should control on |0⟩ and then apply X gates after the operation to restore the original qubit states
            pre_lines = []
            post_lines = []
            for i, bitval in enumerate(onoff):
                if bitval == 0:
                    pre_lines.append(f"x q[{ctrl_qubits[i]}];")
                    post_lines.insert(
                        0, f"x q[{ctrl_qubits[i]}];"
                    )  # reverse order for restoration

            if isinstance(gate.qop, gates.PauliX) and len(ctrl_qubits) == 1:
                mid_line = f"cx q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
            elif isinstance(gate.qop, gates.PauliY) and len(ctrl_qubits) == 1:
                mid_line = f"cy q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
            elif isinstance(gate.qop, gates.PauliZ) and len(ctrl_qubits) == 1:
                mid_line = f"cz q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
            elif isinstance(gate.qop, gates.Hadamard) and len(ctrl_qubits) == 1:
                mid_line = f"ch q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
            elif isinstance(gate.qop, gates.SGate) and len(ctrl_qubits) == 1:
                mid_line = f"cs q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
            elif isinstance(gate.qop, gates.InverseSGate) and len(ctrl_qubits) == 1:
                # Controlled-Sdg (decomposition)
                mid_lines = [
                    f"p(-pi/4) q[{target_qubits[0]}];",
                    f"p(-pi/4) q[{ctrl_qubits[0]}];",
                    f"cx q[{ctrl_qubits[0]}], q[{target_qubits[0]}];",
                    f"p(pi/4) q[{target_qubits[0]}];",
                    f"cx q[{ctrl_qubits[0]}], q[{target_qubits[0]}];",
                ]
                mid_line = "\n".join(mid_lines)
            elif isinstance(gate.qop, gates.CNOT) and len(ctrl_qubits) == 1:
                mid_line = f"ccx q[{ctrl_qubits[0]}], q[{target_qubits[0]}], q[{target_qubits[1]}];"
            elif isinstance(gate.qop, gates.Phase) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"cp({angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.InversePhase) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"cp(-{angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.",
                        gate.qop.name,
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.Rx) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"crx({angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.Ry) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"cry({angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.Rz) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"crz({angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.InverseRx) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"crx(-{angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.InverseRy) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"cry(-{angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.InverseRz) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = (
                        f"crz(-{angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}];"
                    )
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.Rzz) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = f"crzz({angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}], q[{target_qubits[1]}];"
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            elif isinstance(gate.qop, gates.InverseRzz) and len(ctrl_qubits) == 1:
                try:
                    angle = self.values[gate.qop.name]
                    mid_line = f"crzz(-{angle}) q[{ctrl_qubits[0]}], q[{target_qubits[0]}], q[{target_qubits[1]}];"
                except KeyError:
                    logger.error(
                        "Cannot fetch phase angle %s from the backend.", gate.qop.name
                    )
                    raise ValueError(
                        f"Cannot fetch phase angle {gate.qop.name} from the backend."
                    )
            else:  # Multi-controlled gates
                if isinstance(gate.qop, gates.PauliX) and len(ctrl_qubits) == 2:
                    mid_line = f"ccx q[{ctrl_qubits[0]}], q[{ctrl_qubits[1]}], q[{target_qubits[0]}];"
                else:
                    raise NotImplementedError(
                        f"Multi-controlled gate not supported: {gate.qop}"
                    )

            return "\n".join(pre_lines + [mid_line] + post_lines)

        elif isinstance(gate, ClassicalControl):
            onoff = gate.onoff
            ctrl_bits = targets[: len(onoff)]
            target_qubits = targets[len(onoff) :]
            if isinstance(gate.qop, QuantumControl):
                base_line = self.translate_gate(gate.qop, target_qubits)
            else:
                base_line = self.gate_to_qasm(gate.qop, target_qubits)

            # Build the nested if block
            if_blocks = []
            for i, (bit, value) in enumerate(zip(ctrl_bits, onoff)):
                boolean = "true" if value == 1 else "false"
                if_blocks.append(f"if (c[{bit}] == {boolean}) " + "{")

            result = "\n".join(if_blocks)
            result += f"\n    {base_line}"
            result += "\n" + "}" * len(onoff)

            return result

        elif isinstance(gate, Measure):
            if bits is not None:
                return "\n".join(
                    [f"measure q[{q}] -> c[{c}];" for q, c in zip(targets, bits)]
                )
            else:
                logger.error("bits is set to None")

        else:
            return self.gate_to_qasm(gate, targets)

    def define_gate(self, gate_qasm: str) -> str:
        """
        Create the QASM3 code to define seversal gates. These are not standard in QASM3 and must
        be defined before using it.

        Params
        ------
            gate : geqo.core.quantum_operation.QuantumOperation
                A quantum operation. It is checked if it is necessary to generate a definition for it.

        Returns
        -------
            string: String
                The character string corresponding to the gate.
        """
        if gate_qasm == "rzz":
            string = """gate rzz(theta) a, b {
            cx a, b;
            rz(theta) b;
            cx a, b;
        }"""
        elif gate_qasm == "cs":
            string = """gate cs a, b {
            p(pi/4) a;
            p(pi/4) b;
            cx a, b;
            p(-pi/4) b;
            cx a, b;
        }"""
        elif gate_qasm == "crzz":
            string = """gate crzz(theta) a, b, c {
            ccx a, b, c;
            crz(theta) a, c;
            ccx a, b, c;
        }"""

        return string

    def _qasm_lines_init(self, sequence: Sequence) -> list[str]:
        """
        Create the first few lines that are necessary for valid QASM3 code. The input is a ```Sequence``` and it is processed to
        find out whether some definitions are necessary in the beginning of the QASM3 output.

        Params
        ------
            sequence : geqo.core.quantum_circuit.Sequence
                A quantum operation. It is checked if it is necessary to generate a definition for it.

        Returns
        -------
            string: String
                The character string corresponding to the beginning of the QASM3 code.
        """
        seq = embedSequences(sequence)

        lines = ["OPENQASM 3.0; \ninclude 'stdgates.inc';"]

        Gates = [op[0] for op in seq.gatesAndTargets]
        defined = {"rzz": False, "cs": False, "crzz": False}
        for gate in Gates:
            if isinstance(gate, gates.Rzz) and not defined["rzz"]:
                lines.append(self.define_gate("rzz"))
                defined["rzz"] = True
            if isinstance(gate, QuantumControl):
                if isinstance(gate.qop, gates.SGate) and not defined["cs"]:
                    lines.append(self.define_gate("cs"))
                    defined["cs"] = True
                if isinstance(gate.qop, gates.Rzz) and not defined["crzz"]:
                    lines.append(self.define_gate("crzz"))
                    defined["crzz"] = True
            if isinstance(gate, ClassicalControl):
                if isinstance(gate.qop, gates.Rzz) and not defined["rzz"]:
                    lines.append(self.define_gate("rzz"))
                    defined["rzz"] = True
                if isinstance(gate.qop, QuantumControl):
                    if isinstance(gate.qop.qop, gates.SGate) and not defined["cs"]:
                        lines.append(self.define_gate("cs"))
                        defined["cs"] = True
                    if isinstance(gate.qop.qop, gates.Rzz) and not defined["crzz"]:
                        lines.append(self.define_gate("crzz"))
                        defined["crzz"] = True
        return lines

    def _qasm_lines_body(self, sequence: Sequence, lines: list[str]) -> str:
        seq = embedSequences(sequence)

        num_qubits = len(seq.qubits)
        num_clbits = len(seq.bits)

        lines.append(f"qubit[{num_qubits}] q;")
        if num_clbits > 0:
            lines.append(f"bit[{num_clbits}] c;")

        for item in seq.gatesAndTargets:
            if len(item) == 2:
                gate, targets = item
                translate_gate_lines = self.translate_gate(gate, targets)
                if isinstance(translate_gate_lines, str):
                    lines.append(translate_gate_lines)
            elif len(item) == 3:  # Measure
                gate, qubits, bits = item
                translate_gate_lines = self.translate_gate(gate, qubits, bits)
                if isinstance(translate_gate_lines, str):
                    lines.append(translate_gate_lines)

        return "\n".join(lines)

    def sequence_to_qasm3(self, sequence: Sequence) -> str:
        lines = self._qasm_lines_init(sequence)
        qasm_lines = self._qasm_lines_body(sequence, lines)

        return qasm_lines


class sequencer(Simulator):
    """This backend accumulates all gates that were applied. With getSequence() the
    corresponding Sequence object can be obtained.
    """

    def __init__(self, numberBits: int, numberQubits: int):
        self.numberBits = numberBits
        self.numberQubits = numberQubits
        self.seq = []

    def __repr__(self) -> str:
        return "sequencer (#steps so far: " + str(len(self.seq)) + ")"

    def apply(
        self,
        gate: QuantumOperation | str,
        quantumTargets: list[int],
        classicalTargets=None,
    ):
        if classicalTargets is None:
            self.seq.append([gate, quantumTargets])
        else:
            self.seq.append([gate, classicalTargets, quantumTargets])

    def getSequence(self) -> Sequence:
        return Sequence(
            list(range(self.numberBits)), list(range(self.numberQubits)), self.seq
        )


class printer(Simulator):
    def __init__(self, numberQubits: int):
        self.numberQubits = numberQubits
        self.steps = 0

    def __repr__(self) -> str:
        return "printer (#steps so far: " + str(self.steps) + ")"

    def apply(self, gate: QuantumOperation | str, targets: list[int]) -> None:
        self.steps = self.steps + 1
        logger.info(
            "step %s: we apply gate %s to qubits %s",
            self.steps,
            str(gate),
            str(targets),
        )
        return None
