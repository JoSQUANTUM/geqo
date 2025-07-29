from abc import abstractmethod
from itertools import product

import numpy as np

from geqo.__logger__ import get_logger
from geqo.algorithms import PCCM, QFT, InversePCCM, InverseQFT, PermuteQubits
from geqo.core import (
    BasicGate,
    InverseBasicGate,
    Sequence,
)
from geqo.core.quantum_operation import QuantumOperation
from geqo.gates import (
    CNOT,
    Hadamard,
    InversePhase,
    InverseRx,
    InverseRy,
    InverseRz,
    InverseSGate,
    PauliX,
    PauliY,
    PauliZ,
    Phase,
    Rx,
    Ry,
    Rz,
    SGate,
    SwapQubits,
    Toffoli,
)
from geqo.initialization import SetBits, SetDensityMatrix, SetQubits
from geqo.operations import ClassicalControl, DropQubits, Measure, QuantumControl
from geqo.simulators.base import BaseQASM
from geqo.utils._numpy_.helpers import bin2num, permutationMatrixQubitsNumPy

logger = get_logger(__name__)


def getRX(angle: float) -> np.ndarray:
    """
    Return NumPy matrix for Rx gate with given angle.

    Parameters
    ----------
    angle : numpy.float64
        The angle for the rotation.

    Returns
    -------
    matrix : numpy.ndarray
        A NumPy array of size 2x2, which corresponds to a rotation matrix.

    """
    return np.array(
        [
            [np.cos(angle / 2), -1j * np.sin(angle / 2)],
            [-1j * np.sin(angle / 2), np.cos(angle / 2)],
        ]
    )


def getRY(angle: float) -> np.ndarray:
    """
    Return NumPy matrix for Ry gate with given angle.

    Parameters
    ----------
    angle : numpy.float64
        The angle for the rotation.

    Returns
    -------
    matrix : numpy.ndarray
        A NumPy array of size 2x2, which corresponds to a rotation matrix.
    """
    return np.array(
        [
            [np.cos(angle / 2), -np.sin(angle / 2)],
            [np.sin(angle / 2), np.cos(angle / 2)],
        ]
    )


def getUnitaryNumpy(gate: QuantumOperation, values: dict) -> np.ndarray:
    if isinstance(gate, BasicGate):
        if gate.name not in values:
            logger.error("Parameter %s in BasicGate is undefined.", gate.name)
            raise Exception(
                "Parameter " + str(gate.name) + " in BasicGate is undefined."
            )
        return values[gate.name]
    elif type(gate) is InverseBasicGate:
        if gate.name not in values:
            logger.error(
                "Parameter %s in InverseBasicGate is undefined.",
                gate.name,
            )
            raise Exception(
                "Parameter " + str(gate.name) + " in InverseBasicGate is undefined."
            )
        return values[gate.name].conj().T
    elif isinstance(gate, PauliX):
        return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    elif isinstance(gate, PauliY):
        return np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128)
    elif isinstance(gate, PauliZ):
        return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
    elif isinstance(gate, Phase):
        return np.array(
            [[1.0, 0.0], [0.0, np.exp(1j * values[gate.name])]], dtype=np.complex128
        )
    elif isinstance(gate, InversePhase):
        return np.array(
            [[1.0, 0.0], [0.0, np.exp(-1j * values[gate.name])]], dtype=np.complex128
        )
    elif isinstance(gate, Hadamard):
        w2 = 1 / np.sqrt(2)
        return np.array([[w2, w2], [w2, -w2]], dtype=np.complex128)
    elif isinstance(gate, SGate):
        return np.array([[1.0, 0.0], [0.0, 1j]], dtype=np.complex128)
    elif isinstance(gate, InverseSGate):
        return np.array([[1.0, 0.0], [0.0, -1j]], dtype=np.complex128)
    elif isinstance(gate, SwapQubits):
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.complex128,
        )
    elif isinstance(gate, CNOT):
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0, 0.0],
            ],
            dtype=np.complex128,
        )
    elif isinstance(gate, PermuteQubits):
        qubits = list(range(len(gate.targetOrder)))
        perm = permutationMatrixQubitsNumPy([gate.targetOrder.index(q) for q in qubits])
        return perm
    elif isinstance(gate, QuantumControl):
        u = getUnitaryNumpy(gate.qop, values)
        size = u.shape[0]
        dim = 2 ** len(gate.onoff) * size
        target_state_num = bin2num(gate.onoff)
        res = np.eye(dim, dtype=u.dtype)
        start = target_state_num * size
        end = start + size
        res[start:end, start:end] = u
        return res
    elif isinstance(gate, Rx):
        return getRX(values[gate.name])
    elif isinstance(gate, InverseRx):
        return getRX(-values[gate.name])
    elif isinstance(gate, Ry):
        return getRY(values[gate.name])
    elif isinstance(gate, InverseRy):
        return getRY(-values[gate.name])
    elif isinstance(gate, Rz):
        return np.array(
            [
                [np.exp(-1j * values[gate.name] / 2), 0.0],
                [0.0, np.exp(1j * values[gate.name] / 2)],
            ],
            dtype=np.complex128,
        )
    elif isinstance(gate, InverseRz):
        return np.array(
            [
                [np.exp(1j * values[gate.name] / 2), 0.0],
                [0.0, np.exp(-1j * values[gate.name] / 2)],
            ],
            dtype=np.complex128,
        )
    else:
        logger.error("gate %s not implemented yet", gate)
        raise Exception("gate " + str(gate) + " not implemented yet")


class BaseSimulatorNumpy(BaseQASM):
    def __init__(self, numberBits: int, numberQubits: int, values: dict):
        """
        The constructor of this simulator takes as parameters the number of classical bits, the number of qubits
        and a list of values, which are needed to run all operations.

        Parameters
        ----------
        numberBits : int
            The number of classical bits of the simulated system.
        numberQubits : int
            The number of qubits of the simulated system.
        values : {key:value}
            A dictionary of keys and values, which are needed for simulating the operations.

        Returns
        -------
        BaseSimulatorNumpy : geqo.simulators.numpy.BaseSimulatorNumpy
            A simulator object, which is based on NumPy.
        """
        self.numberBits = numberBits
        self.numberQubits = numberQubits
        super().__init__(values)

    @abstractmethod
    def prepareBackend(self, operations: list[QuantumOperation]):
        """
        For a list of supported operators, this method sets the necessary values for the simulator.

        Parameters
        ----------
        operations : list(geqo.core.quantum_operation.QuantumOperation)
            A list of quantum operations, for which the backend should be prepared.
        """
        pass

    @abstractmethod
    def applyUmatrixNumpy(
        self,
        u: np.ndarray,
        targets: list[int],
        extraControls: dict | list[int] | None = None,
    ):
        """
        Apply a unitary matrix to the state, which is currently kept in the simulator. For recursion, a list of extra control qubits can be defined.

        Parameters
        ----------
        u : numpy.ndarray
            A unitary matrix.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided unitary matrix.
        extraControls : list(int)
            A list of indexes, which are taken as control qubits.
        """
        pass

    @abstractmethod
    def apply(self, gate: QuantumOperation, targets: list[int], *args, **kwargs):
        """
        Apply an operation to the state, which is currently kept in the simulator.

        Parameters
        ----------
        gate : geqo.core.quantum_operation.QuantumOperation
            The operation that should be applied.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided operation.
        """
        pass

    def setValue(self, name: str, value: float | list[int] | np.ndarray | np.float64):
        """
        Set a name to a specific value. This has to be done before an operationen, which contains the name, can be applied.

        Parameters
        ----------
        name : String
            The name, which is set to a value.
        value : numpy.float64 | numpy.ndarray
            The corresponding value for the name.
        """
        self.values[name] = value

    def sequence_to_qasm3(self, sequence: Sequence) -> str:
        """
        Turn a ```Sequence``` to a QASM sequence, which is a character string.

        Parameters
        ----------
        sequence : geqo.core.quantum_circuit.Sequence
            The name, which is set to a value.

        Returns
        -------
        qasm_lines : String
            A character string, which is a QASM representation of the provided ```Sequence```.
        """
        lines = self._qasm_lines_init(sequence)
        qasm_lines = self._qasm_lines_body(sequence, lines)

        return qasm_lines


class simulatorStatevectorNumpy(BaseSimulatorNumpy):
    def __init__(self, numberBits: int, numberQubits: int):
        """
        The constructor of this simulator takes as parameters the number of classical bits, the number of qubits
        and a list of values, which are needed to run all operations.

        Parameters
        ----------
        numberBits : int
            The number of classical bits of the simulated system.
        numberQubits : int
            The number of qubits of the simulated system.

        Returns
        -------
        self : geqo.simulators.numpy.simulatorStatevectorNumpy
            A simulator object, which is based on NumPy.
        """
        values = {}
        super().__init__(numberBits, numberQubits, values)
        if self.numberQubits > 32:
            raise NotImplementedError("Too many qubits, limit is 32")

        self.state = np.zeros(shape=(2**self.numberQubits, 1), dtype=np.complex128)

        self.state[0, 0] = 1.0 + 0 * 1j

        self.measurementResult = {}
        self.measurementHappened = False

        self.classicalBits = [0] * numberBits

    def __repr__(self) -> str:
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f"{self.__class__.__name__}({self.numberBits}, {self.numberQubits})"

    def prepareBackend(self, operations: list[QuantumOperation]):
        """
        For a list of supported operators, this method sets the necessary values for the simulator.

        Parameters
        ----------
        operations : list(geqo.core.quantum_operation.QuantumOperation)
            A list of quantum operations, for which the backend should be prepared.
        """
        for ops in operations:
            if isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")

                self.values[ops.nameSpacePrefix + "RX(π/2)"] = np.pi / 2
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = -np.pi / 2
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = -np.pi / 2
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    logger.warning("%s not specified in the backend.", nameAngle)
                else:
                    logger.debug(
                        "found nameAngle %s with value %s",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    self.values[ops.nameSpacePrefix + "RX(" + str(nameAngle) + ")"] = (
                        self.values[nameAngle]
                    )
            elif isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * np.pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])

            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])

            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = np.pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -np.pi / 4
            else:
                logger.error("prepareBackend: operation not supported: %s", str(ops))
                raise Exception("prepareBackend: operation not supported:", str(ops))

    def applyUmatrixNumpy(
        self,
        u: np.ndarray,
        targets: list[int],
        extraControls: dict | list[int] | None = None,
    ):
        """
        Apply a unitary matrix to the state, which is currently kept in the simulator. For recursion, a list of extra control qubits can be defined.

        Parameters
        ----------
        u : numpy.ndarray
            A unitary matrix.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided unitary matrix.
        extraControls : list(int)
            A list of indexes, which are taken as control qubits.
        """
        non_targets = list(set(range(self.numberQubits)) - set(targets))

        for nt in product([0, 1], repeat=len(non_targets)):
            # check that the inherited controls are all set
            isControlled = True
            if isinstance(extraControls, list):
                for x in extraControls:
                    if not (nt[non_targets.index(x)] == extraControls[x]):
                        isControlled = False
            if isControlled:
                affected_components = []
                for t in product([0, 1], repeat=len(targets)):
                    bitstring = np.zeros(shape=self.numberQubits, dtype=int)
                    bitstring[non_targets] = nt
                    bitstring[targets] = t
                    affected_components.append(int("".join(map(str, bitstring)), 2))
                self.state[affected_components] = u @ self.state[affected_components]

    def apply(
        self,
        gate: QuantumOperation,
        targets: list[int],
        classicalTargets=None,
    ):
        """
        Apply an operation to the state, which is currently kept in the simulator.

        Parameters
        ----------
        gate : geqo.core.quantum_operation.QuantumOperation
            The operation that should be applied.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided operation.
        classicalTargets : list(int)
            The list of classical bits, which are the target of the provided operation, e.g. a measurement.
        extraControls : list(int)
            A list of qubit indices. The qubits are used as control qubits. Note that this is only for internal use.
        """
        if classicalTargets is None:
            classicalTargets = []

        if self.measurementHappened:
            logger.error("no more operation allowed after measurement")
            raise Exception("no more operation allowed after measurement")

        if isinstance(gate, ClassicalControl):
            logger.error("cannot perform ClassicalControl in statevector simulations")
            raise Exception(
                "cannot perform ClassicalControl in statevector simulations"
            )

        elif gate.hasDecomposition():
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            for x in range(len(dec.qubits)):
                qubitMapping[dec.qubits[x]] = targets[x]

            bitMapping = {}
            for x in range(len(dec.bits)):
                bitMapping[dec.bits[x]] = classicalTargets[x]

            for d in dec.gatesAndTargets:
                if len(d) == 2:
                    key_type = type(dec.qubits[0])
                    apply_targets = [
                        qubitMapping[x]
                        if type(x) is key_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                    self.apply(d[0], apply_targets)
                else:
                    # classical and quantum bits; quantum first
                    qkey_type = type(dec.qubits[0])
                    apply_qtargets = [
                        qubitMapping[x]
                        if type(x) is qkey_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                    ckey_type = type(dec.bits[0])
                    apply_ctargets = [
                        bitMapping[x]
                        if type(x) is ckey_type
                        else bitMapping[dec.bits[x]]
                        for x in d[2]
                    ]
                    self.apply(
                        d[0],
                        apply_qtargets,
                        apply_ctargets,
                    )

        elif gate.isUnitary():
            u = getUnitaryNumpy(gate, self.values)
            non_targets = list(set(range(self.numberQubits)) - set(targets))
            dim = len(self.state)

            new_state = np.zeros((dim, 1), dtype=np.complex128)

            for n in product([0, 1], repeat=len(non_targets)):
                applied_indices = []
                for t in product([0, 1], repeat=len(targets)):
                    power_t = 2 ** np.array(
                        [self.numberQubits - 1 - tar for tar in targets]
                    )
                    power_n = 2 ** np.array(
                        [self.numberQubits - 1 - non for non in non_targets]
                    )
                    index = np.dot(np.array(t), power_t) + np.dot(np.array(n), power_n)
                    applied_indices.append(index)
                # only apply u to the subspace of the target qubits
                applied_indices = np.array(applied_indices).astype(np.int64)
                new_state[applied_indices] = u @ self.state[applied_indices]

            self.state = new_state

        elif isinstance(gate, Measure):
            if len(targets) != gate.numberQubits:
                raise ValueError(
                    "Number of targets does not match number of measured qubits"
                )

            self.measurementHappened = True

            probabilities = dict()

            non_targets = list(set(range(self.numberQubits)) - set(targets))

            for t in product([0, 1], repeat=gate.numberQubits):
                probability = 0.0
                bitstring = np.zeros(shape=self.numberQubits, dtype=int)
                bitstring[targets] = t
                for nt in product([0, 1], repeat=len(non_targets)):
                    bitstring[non_targets] = nt
                    coeff = self.state[int("".join(map(str, bitstring)), 2), 0]
                    probability += coeff * np.conj(coeff)

                newClassicalBits = self.classicalBits
                for i in range(len(classicalTargets)):
                    newClassicalBits[classicalTargets[i]] = t[i]

                probabilities[tuple(newClassicalBits)] = np.real(probability)

            self.measurementResult = probabilities

        elif isinstance(gate, SetBits):
            bits = self.values.get(gate.name, None)

            if bits is None:
                logger.error('Bit values "%s" not found', gate.name)
                raise ValueError(f'Bit values "{gate.name}" not found')

            if len(classicalTargets) != len(bits):
                logger.error("wrong number of bits in definition for SetBits")
                raise ValueError("wrong number of bits in definition for SetBits")

            for i in range(len(classicalTargets)):
                self.classicalBits[classicalTargets[i]] = bits[i]

        elif isinstance(gate, SetQubits):
            logger.error("cannot set qubits in statevector simulations")
            raise Exception("cannot set qubits in statevector simulations")

        elif isinstance(gate, DropQubits):
            logger.error("cannot drop qubits in statevector simulations")
            raise Exception("cannot drop qubits in statevector simulations")

        elif isinstance(gate, SetDensityMatrix):
            logger.error("cannot set density matrix in statevector simulations")
            raise Exception("cannot set density matrix in statevector simulations")
        else:
            logger.error("gate not supported: %s", gate)
            raise Exception("gate not supported:", str(gate))
