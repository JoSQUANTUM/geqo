import itertools
from abc import abstractmethod

import sympy as sym
from sympy import Mul, MutableDenseMatrix, S, Symbol, pi, re
from sympy.physics.quantum import TensorProduct

from geqo.__logger__ import get_logger
from geqo.algorithms import PermuteQubits
from geqo.algorithms.algorithms import PCCM, QFT, InversePCCM, InverseQFT
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
    InverseRzz,
    InverseSGate,
    PauliX,
    PauliY,
    PauliZ,
    Phase,
    Rx,
    Ry,
    Rz,
    Rzz,
    SGate,
    SwapQubits,
    Toffoli,
)
from geqo.initialization import SetBits, SetDensityMatrix, SetQubits
from geqo.operations import (
    ClassicalControl,
    DropQubits,
    Measure,
    QuantumControl,
)
from geqo.simulators.base import BaseQASM
from geqo.utils import (
    bin2num,
    partial_diag,
    permutationMatrixQubitsSymPy,
)
from geqo.utils._sympy_.helpers import (
    multiQubitsUnitary,
    partialTrace,
    projection,
)

logger = get_logger(__name__)


def getRX(angle: float) -> MutableDenseMatrix:
    """
    Return a SymPy matrix for Rx gate with given angle.

    Parameters
    ----------
    angle : sympy.core.basic.Basic
        The angle for the rotation.

    Returns
    -------
    matrix : sympy.Matrix
        A SymPy array of size 2x2, which corresponds to a rotation matrix.

    """
    return sym.Matrix(
        [
            [sym.cos(angle / 2), -sym.I * sym.sin(angle / 2)],
            [-sym.I * sym.sin(angle / 2), sym.cos(angle / 2)],
        ]
    )


def getRY(angle: float) -> MutableDenseMatrix:
    """
    Return a SymPy matrix for Ry gate with given angle.

    Parameters
    ----------
    angle : sympy.core.basic.Basic
        The angle for the rotation.

    Returns
    -------
    matrix : sympy.Matrix
        A SymPy array of size 2x2, which corresponds to a rotation matrix.

    """
    return sym.Matrix(
        [
            [sym.cos(angle / 2), -sym.sin(angle / 2)],
            [sym.sin(angle / 2), sym.cos(angle / 2)],
        ]
    )


def getUnitarySymPy(gate: QuantumOperation, values: dict) -> dict | MutableDenseMatrix:
    """
    Get the matrix representation for the different quantum operations. If there is a name for a parameter in a gate, then it is retrieved from the values parameter.

    Parameters
    ----------
    gate : geqo.core.quantum_operation.QuantumOperation
        A quantum operation that should be converted to matrix form.
    values : dict([String, sympy.core.basic.Basic])
        A dictionary that assigns a SymPy value to names.

    Returns
    -------
    res : sympy.Matrix
        The matrix corresponding to the provided quantum operation.
    """
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
        return sym.conjugate(values[gate.name]).T
    elif isinstance(gate, PauliX):
        return sym.Matrix([[0, 1], [1, 0]])
    elif isinstance(gate, PauliY):
        return sym.Matrix([[0, -sym.I], [sym.I, 0]])
    elif isinstance(gate, PauliZ):
        return sym.Matrix([[1, 0], [0, -1]])
    elif isinstance(gate, Phase):
        return sym.Matrix([[1, 0], [0, sym.exp(sym.I * values[gate.name])]])
    elif isinstance(gate, InversePhase):
        return sym.Matrix([[1, 0], [0, sym.exp(-sym.I * values[gate.name])]])
    elif isinstance(gate, Hadamard):
        w2 = 1 / sym.sqrt(2)
        return sym.Matrix([[w2, w2], [w2, -w2]])
    elif isinstance(gate, SGate):
        return sym.Matrix([[1, 0], [0, sym.I]])
    elif isinstance(gate, InverseSGate):
        return sym.Matrix([[1, 0], [0, -sym.I]])
    elif isinstance(gate, SwapQubits):
        return sym.Matrix([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    elif isinstance(gate, CNOT):
        return sym.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    elif isinstance(gate, PermuteQubits):
        qubits = list(range(len(gate.targetOrder)))
        perm = permutationMatrixQubitsSymPy([gate.targetOrder.index(q) for q in qubits])
        return perm
    elif isinstance(gate, QuantumControl):
        u = getUnitarySymPy(gate.qop, values)
        size = u.shape[0]
        res = sym.Matrix([])
        for t in list(itertools.product([0, 1], repeat=len(gate.onoff))):
            if t == tuple(gate.onoff):
                res = sym.diag(res, u)
            else:
                res = sym.diag(res, sym.eye(size))
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
        return sym.Matrix(
            [
                [sym.exp(-sym.I * values[gate.name] / 2), 0],
                [0, sym.exp(sym.I * values[gate.name] / 2)],
            ]
        )
    elif isinstance(gate, InverseRz):
        return sym.Matrix(
            [
                [sym.exp(sym.I * values[gate.name] / 2), 0],
                [0, sym.exp(-sym.I * values[gate.name] / 2)],
            ]
        )
    elif isinstance(gate, Rzz):
        return sym.Matrix(
            [
                [sym.exp(-sym.I * values[gate.name] / 2), 0, 0, 0],
                [0, sym.exp(sym.I * values[gate.name] / 2), 0, 0],
                [0, 0, sym.exp(sym.I * values[gate.name] / 2), 0],
                [0, 0, 0, sym.exp(-sym.I * values[gate.name] / 2)],
            ]
        )
    elif isinstance(gate, InverseRzz):
        return sym.Matrix(
            [
                [sym.exp(sym.I * values[gate.name] / 2), 0, 0, 0],
                [0, sym.exp(-sym.I * values[gate.name] / 2), 0, 0],
                [0, 0, sym.exp(-sym.I * values[gate.name] / 2), 0],
                [0, 0, 0, sym.exp(sym.I * values[gate.name] / 2)],
            ]
        )
    else:
        logger.error("gate %s not implemented yet", gate)
        raise Exception("gate " + str(gate) + " not implemented yet")


class BaseSympySimulator(BaseQASM):
    def __init__(self, numberQubits: int, values: dict):
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
        BaseSympySimulator : geqo.simulators.sympy.BaseSympySimulator
            A simulator object, which is based on SymPy.
        """
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
    def apply(self, gate: QuantumOperation, targets: list[int], *args, **kwargs):
        """
        Apply an operation to the quantum state, which is currently kept in the simulator.

        Parameters
        ----------
        gate : geqo.core.quantum_operation.QuantumOperation
            The operation that should be applied.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided operation.
        """
        pass

    def setValue(self, name: str, value: list | Symbol | MutableDenseMatrix | float):
        """
        Set a name to a specific value. This has to be done before an operationen, which contains the name, can be applied.

        Parameters
        ----------
        name : String
            The name, which is set to a value.
        value : sympy.Matrix | sympy.core.basic.Basic
            The corresponding value for the name.
        """
        self.values[name] = value

    def _qasm_lines_sympy(self, lines: list[str]) -> list[str]:
        appeared = []
        for key, item in self.values.items():
            if isinstance(item, (Symbol, Mul)):
                if item.has(pi):
                    self.values[key] = float(item)
                elif item not in appeared:
                    lines.append(f"input float {item};")
                    appeared.append(item)
        return lines

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
        lines = self._qasm_lines_sympy(lines)
        qasm_lines = self._qasm_lines_body(sequence, lines)

        return qasm_lines


class ensembleSimulatorSymPy(BaseSympySimulator):
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
        self : geqo.simulators.sympy.ensembleSimulatorSymPy
            A simulator object, which is based on SymPy.
        """
        values = {}
        super().__init__(numberQubits, values)
        self.numberBits = numberBits
        rho = sym.zeros(2**self.numberQubits, 2**self.numberQubits)
        rho[0, 0] = 1
        self.ensemble = {}
        bits = (0,) * self.numberBits
        self.ensemble[bits] = (1, rho)

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
            if isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * S.Pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])
            elif isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")
                self.values[ops.nameSpacePrefix + "RX(π/2)"] = (
                    S.Pi / 2
                )  # getRX(S.Pi / 2)
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = (
                    -S.Pi / 2
                )  # getRX(-S.Pi / 2)
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = (
                    -S.Pi / 2
                )  # getRY(-S.Pi / 2)
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    phi = sym.Symbol(nameAngle)
                    self.values[ops.nameSpacePrefix + "RX(" + str(phi) + ")"] = (
                        phi  # getRX(
                    )
                    # )
                # phi
                else:
                    logger.debug(
                        "found nameAngle %s with value %s ",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    phi = sym.Symbol(nameAngle)
                    self.values[ops.nameSpacePrefix + "RX(" + str(phi) + ")"] = (
                        self.values[nameAngle]
                    )  # getRX(
                    # self.values[nameAngle]
                    # )

            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])
            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = S.Pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -S.Pi / 4
            else:
                logger.error("prepareBackend: operation not supported: %s", ops)
                raise Exception("prepareBackend: operation not supported:", str(ops))

    def apply(
        self,
        gate: QuantumOperation,
        targets: list[int],
        classicalTargets: list[int] | None = None,
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
            The list of classical bits, which are the target of the provided operation.
        """
        if classicalTargets is None:
            classicalTargets = []

        if isinstance(gate, ClassicalControl):
            if gate.qop.isUnitary():
                controls = targets[: -gate.qop.getNumberQubits()]  # control bits
                target_qubits = targets[-gate.qop.getNumberQubits() :]
                onoffMapping = [controls.index(t) for t in sorted(controls)]
                condition = [gate.onoff[i] for i in onoffMapping]

                newEnsemble = {}
                for s in self.ensemble:
                    bits = [s[i] for i in range(self.numberBits) if i in controls]
                    if bits == condition:  # if the control condition is met
                        dec = gate.qop.getEquivalentSequence()
                        qubitMapping = {}
                        qubits = [*range(len(dec.qubits))]
                        for x in range(len(dec.qubits)):
                            qubitMapping[qubits[x]] = target_qubits[x]

                        unitaries = sym.eye(2**self.numberQubits)
                        for d in dec.gatesAndTargets:
                            # if len(d) == 2:  # non measurement
                            op = d[0]
                            subtargets = [qubitMapping[x] for x in d[1]]

                            if (
                                op.hasDecomposition()
                            ):  # i.e. QubitReversal within QFT still has decomposition
                                dec2 = op.getEquivalentSequence()
                                qubitMapping2 = {}
                                qubits2 = [*range(len(dec2.qubits))]
                                for x in range(len(dec2.qubits)):
                                    qubitMapping2[qubits2[x]] = subtargets[x]

                                for d2 in dec2.gatesAndTargets:
                                    op2 = d2[0]
                                    subtargets2 = [qubitMapping2[x] for x in d2[1]]

                                    u = multiQubitsUnitary(
                                        getUnitarySymPy(op2, self.values),
                                        [*range(self.numberQubits)],
                                        subtargets2,
                                    )
                                    unitaries = u * unitaries
                            else:  # no more decomposition after first decomposition
                                u = multiQubitsUnitary(
                                    getUnitarySymPy(op, self.values),
                                    [*range(self.numberQubits)],
                                    subtargets,
                                )
                                unitaries = u * unitaries
                            # else:  # measurement
                            #    raise Exception(
                            #        "Controlled measurements are not supported."
                            #    )

                        newEnsemble[s] = (
                            self.ensemble[s][0],
                            unitaries
                            * self.ensemble[s][1]
                            * sym.conjugate(unitaries.T),
                        )

                    else:  # if the control condition is not met
                        newEnsemble[s] = (
                            self.ensemble[s][0],
                            self.ensemble[s][1],
                        )
                self.ensemble = newEnsemble
            else:  # non-unitary target operation
                logger.error("Controlled operations cannot be non-unitary.")
                raise Exception("Controlled operations cannot be non-unitary.")

        # If there is a decomposition into a sequence of other gates, then use it.
        elif gate.hasDecomposition():
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            if dec is not None:
                for x in range(len(dec.qubits)):
                    qubitMapping[dec.qubits[x]] = targets[x]

                bitMapping = {}
                for x in range(len(dec.bits)):
                    bitMapping[dec.bits[x]] = classicalTargets[x]

                for d in dec.gatesAndTargets:
                    if len(d) == 2:
                        # only qubits
                        if isinstance(d[0], ClassicalControl):
                            ckey_type = type(dec.bits[0])
                            qkey_type = type(dec.qubits[0])
                            controls = d[1][: len(d[0].onoff)]
                            qtargets = d[1][len(d[0].onoff) :]
                            control_targets = [
                                bitMapping[x]
                                if type(x) is ckey_type
                                else bitMapping[dec.bits[x]]
                                for x in controls
                            ]
                            quantum_targets = [
                                qubitMapping[x]
                                if type(x) is qkey_type
                                else qubitMapping[dec.qubits[x]]
                                for x in qtargets
                            ]
                            apply_targets = control_targets + quantum_targets
                        else:
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
                            # [qubitMapping[x] for x in d[1]],
                            # [bitMapping[x] for x in d[2]],
                            apply_qtargets,
                            apply_ctargets,
                        )

        # If the gate is unitary, then get the matrix and
        # apply it to the right order of qubits.
        elif gate.isUnitary():
            targetOrder = [q for q in targets]
            for q in list(range(self.numberQubits)):
                if q not in targetOrder:
                    targetOrder.append(q)

            perm = permutationMatrixQubitsSymPy(
                [targetOrder.index(q) for q in list(range(self.numberQubits))]
            )

            u = getUnitarySymPy(gate, self.values)
            u2 = TensorProduct(u, sym.eye(2 ** (self.numberQubits - len(targets))))
            u3 = perm.T * u2 * perm
            newEnsemble = {}
            for s in self.ensemble:
                densityMatrix = self.ensemble[s][1]
                densityMatrix2 = u3 * densityMatrix * sym.conjugate(u3.T)
                newEnsemble[s] = (self.ensemble[s][0], densityMatrix2)
            self.ensemble = newEnsemble

        elif isinstance(gate, SetDensityMatrix):
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            newDensityMatrix = self.values[gate.name]

            # trace out the target qubits
            newEnsemble = {}
            for ens in self.ensemble:
                prob = self.ensemble[ens][0]
                rho = self.ensemble[ens][1]
                rho_part, perm = partialTrace(
                    rho, list(range(self.numberQubits)), targets
                )
                rho2 = (perm.T) * TensorProduct(rho_part, newDensityMatrix) * perm
                newEnsemble[ens] = (prob, rho2)
            self.ensemble = newEnsemble
        elif isinstance(gate, Measure):
            targetOrder = [q for q in targets]
            for q in list(range(self.numberQubits)):
                if q not in targetOrder:
                    targetOrder.append(q)

            perm = permutationMatrixQubitsSymPy(
                [targetOrder.index(q) for q in list(range(self.numberQubits))]
            )

            newEnsemble = {}
            for s in self.ensemble:
                currentProb = self.ensemble[s][0]
                currentRho = perm * self.ensemble[s][1] * perm.T

                # Create all projectors, we assume that the measured
                # qubits are now at the front.
                numberMeasuredQubits = len(targets)
                for t in itertools.product([0, 1], repeat=numberMeasuredQubits):
                    part1 = sym.zeros(2**numberMeasuredQubits, 2**numberMeasuredQubits)
                    part1[bin2num(t), bin2num(t)] = 1
                    part2 = sym.eye(2 ** (self.numberQubits - numberMeasuredQubits))
                    proj = TensorProduct(part1, part2)
                    resultProb = re(sym.trace(proj * currentRho))
                    resultRho = perm.T * proj * currentRho * proj * perm
                    newBits = [x for x in s]  # make a copy
                    for ti in range(len(t)):
                        newBits[classicalTargets[ti]] = t[ti]
                    newBits = tuple(newBits)

                    if resultProb > 0:
                        # if True:
                        resultRho = resultRho / resultProb
                        if newBits in newEnsemble:
                            previousProb = newEnsemble[newBits][0]
                            previousRho = newEnsemble[newBits][1]
                            newEnsemble[newBits] = (
                                resultProb * currentProb + previousProb,
                                (
                                    previousProb * previousRho
                                    + resultProb * currentProb * resultRho
                                )
                                / (resultProb * currentProb + previousProb),
                            )
                        else:
                            newEnsemble[newBits] = (
                                resultProb * currentProb,
                                resultRho,
                            )

            self.ensemble = newEnsemble

        elif type(gate) is SetBits:
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )
            bitValues = self.values[gate.name]

            newEnsemble = {}
            for s in self.ensemble:
                prob = self.ensemble[s][0]
                rho = self.ensemble[s][1]

                # set the bits as defined in SetBits. We must respect a bitMapping
                s2 = [x for x in s]
                for ti in range(len(targets)):
                    s2[targets[ti]] = bitValues[ti]
                s3 = tuple(s2)

                if s3 not in newEnsemble:
                    newEnsemble[s3] = (prob, rho)
                else:
                    previousProb = newEnsemble[s3][0]
                    previousRho = newEnsemble[s3][1]

                    newEnsemble[s3] = (
                        prob + previousProb,
                        (previousProb * previousRho + prob * rho)
                        / (previousProb + prob),
                    )
            self.ensemble = newEnsemble

        elif type(gate) is SetQubits:
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            qubitValues = self.values[gate.name]
            newDensityMatrix = sym.zeros(2 ** len(targets), 2 ** len(targets))
            index = bin2num(qubitValues)
            newDensityMatrix[index, index] = 1

            # trace out the target qubits
            newEnsemble = {}
            for ens in self.ensemble:
                prob = self.ensemble[ens][0]
                rho = self.ensemble[ens][1]
                rho_part, perm = partialTrace(
                    rho, list(range(self.numberQubits)), targets
                )
                rho2 = (perm.T) * TensorProduct(rho_part, newDensityMatrix) * perm
                newEnsemble[ens] = (prob, rho2)
            self.ensemble = newEnsemble

        elif type(gate) is DropQubits:
            # trace out the dropped qubits
            newEnsemble = {}
            for ens in self.ensemble:
                prob = self.ensemble[ens][0]
                rho = self.ensemble[ens][1]
                rho_reduced, _ = partialTrace(
                    rho, list(range(self.numberQubits)), targets
                )
                newEnsemble[ens] = (prob, rho_reduced)

            self.ensemble = newEnsemble
            self.numberQubits -= len(targets)

        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )


class mixedStateSimulatorSymPy(ensembleSimulatorSymPy):
    def __init__(
        self, numberBits: int, numberQubits: int, return_density: bool = False
    ):
        """
        The constructor of this simulator takes as parameters the number of classical bits, the number of qubits
        and a list of values, which are needed to run all operations.

        Parameters
        ----------
        numberBits : int
            The number of classical bits of the simulated system.
        numberQubits : int
            The number of qubits of the simulated system.
        return_density : Bool
            Should the full history of density matrices after measurements be preserved?

        Returns
        -------
        self : geqo.simulators.sympy.mixedStateSimulatorSymPy
            A simulator object, which is based on SymPy.
        """
        super().__init__(numberBits, numberQubits)
        rho = sym.zeros(2**self.numberQubits, 2**self.numberQubits)
        rho[0, 0] = 1
        self.densityMatrix = rho
        self.measureHistory = []
        self.return_density = return_density

    def apply(
        self,
        gate: QuantumOperation,
        targets: list[int],
        classicalTargets: list[int] | None = None,
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
            The list of classical bits, which are the target of the provided operation.
        """
        if classicalTargets is None:
            classicalTargets = []
        # If there is a decomposition into a sequence of other gates, then use it.
        if gate.hasDecomposition() is True:
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            if dec is not None:
                for x in range(len(dec.qubits)):
                    qubitMapping[dec.qubits[x]] = targets[x]

                bitMapping = {}
                for x in range(len(dec.bits)):
                    bitMapping[dec.bits[x]] = classicalTargets[x]

                for d in dec.gatesAndTargets:
                    if len(d) == 2:
                        # only qubits
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
                            # [qubitMapping[x] for x in d[1]],
                            # [bitMapping[x] for x in d[2]],
                            apply_qtargets,
                            apply_ctargets,
                        )

        # If the gate is unitary, then get the matrix and
        # apply it to the right order of qubits.
        elif gate.isUnitary():
            u = getUnitarySymPy(gate, self.values)

            u_perm = multiQubitsUnitary(u, [*range(self.numberQubits)], targets)

            self.densityMatrix = u_perm * self.densityMatrix * sym.conjugate(u_perm.T)

        elif isinstance(gate, SetDensityMatrix):
            if gate.name not in self.values:
                logger.error(
                    "name of parameter %s not known to simulator",
                    gate.name,
                )
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            newDensityMatrix = self.values[gate.name]

            # trace out the target qubits
            rho_part, perm = partialTrace(
                self.densityMatrix, list(range(self.numberQubits)), targets
            )
            self.densityMatrix = (
                (perm.T) * TensorProduct(rho_part, newDensityMatrix) * perm
            )

        elif isinstance(gate, Measure):
            non_target = list(set(list(range(self.numberQubits))) - set(targets))

            outcome = partial_diag(
                self.densityMatrix, list(range(self.numberQubits)), non_target
            )

            # Ensemble now stores only the probability of each measurement outcome and optionally the mixed density matrices
            # measurement = {(0,0,0):0.5,(1,1,1):0.5,"mixed_state":density_matrix}
            measurement = {}
            mixedRho = sym.zeros(2**self.numberQubits, 2**self.numberQubits)

            for out in outcome:
                resultProb = out[1]

                resultRho = projection(
                    self.densityMatrix, self.numberQubits, targets, out[0]
                )

                mixedRho += resultRho

                measurement[out[0]] = re(resultProb)

            if self.return_density:
                measurement["mixed_state"] = mixedRho

            self.densityMatrix = mixedRho
            self.measureHistory.append(measurement)

        elif isinstance(gate, SetBits):
            logger.error("SetBits not supported by this simulator")
            raise Exception("SetBits not supported by this simulator")

        elif isinstance(gate, SetQubits):
            if gate.name not in self.values:
                logger.error("name of parameter %s not known to simulator", gate.name)
                raise Exception(
                    "name of parameter " + str(gate.name) + " not known to simulator"
                )

            qubitValues = self.values[gate.name]
            newDensityMatrix = sym.zeros(2 ** len(targets), 2 ** len(targets))
            index = bin2num(qubitValues)
            newDensityMatrix[index, index] = 1

            # trace out the target qubits and re-combine with newDensityMatrix
            rho_part, perm = partialTrace(
                self.densityMatrix, list(range(self.numberQubits)), targets
            )
            self.densityMatrix = (
                (perm.T) * TensorProduct(rho_part, newDensityMatrix) * perm
            )

        elif isinstance(gate, DropQubits):
            # trace out the dropped qubits
            rho_reduced, _ = partialTrace(
                self.densityMatrix, list(range(self.numberQubits)), targets
            )

            self.densityMatrix = rho_reduced
            self.numberQubits -= len(targets)

        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )


class simulatorUnitarySymPy(BaseSympySimulator):
    """Calculate the unitary matrix corresponding to a sequence of
    gates. No non-unitary operations like ClassicalControl, Measurement
    or DropQubits are allowed.
    """

    def __init__(self, numberQubits: int):
        """
        The constructor of this simulator takes as parameters the number of qubits.

        Parameters
        ----------
        numberQubits : int
            The number of qubits of the simulated system.

        Returns
        -------
        self : geqo.simulators.sympy.simulatorUnitarySymPy
            A simulator object, which is based on SymPy.
        """
        values = {}
        super().__init__(numberQubits, values)
        self.u = sym.eye(2**self.numberQubits)

    def __repr__(self) -> str:
        """
        Returns
        -------
        string_representation : String
            Representation of the object as character string.
        """
        return f"{self.__class__.__name__}({self.numberQubits})"

    def prepareBackend(self, operations: list[QuantumOperation]):
        """
        For a list of supported operators, this method sets the necessary values for the simulator.

        Parameters
        ----------
        operations : list(geqo.core.quantum_operation.QuantumOperation)
            A list of quantum operations, for which the backend should be prepared.
        """
        for ops in operations:
            if isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * S.Pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])
            elif isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")
                self.values[ops.nameSpacePrefix + "RX(π/2)"] = (
                    S.Pi / 2
                )  # getRX(S.Pi / 2)
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = (
                    -S.Pi / 2
                )  # getRX(-S.Pi / 2)
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = (
                    -S.Pi / 2
                )  # getRY(-S.Pi / 2)
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    phi = sym.Symbol(nameAngle)
                    self.values[ops.nameSpacePrefix + "RX(" + str(phi) + ")"] = (
                        phi  # getRX(
                    )
                    # )
                # phi
                else:
                    logger.debug(
                        "found nameAngle %s with value %s",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    phi = sym.Symbol(nameAngle)
                    self.values[ops.nameSpacePrefix + "RX(" + str(phi) + ")"] = (
                        self.values[nameAngle]
                    )  # getRX(
                    # self.values[nameAngle]
                    # )
            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])
            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = S.Pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -S.Pi / 4
            else:
                logger.error("operation not supported: %s", ops)
                raise Exception("operation not supported:", str(ops))

    def apply(self, gate: QuantumOperation, targets: list[int]):
        """
        Calculate the updated unitary matrix, which is currently kept in the simulator, when the operation is executed. The unitary matrix is based on the order of applying operations.

        Parameters
        ----------
        gate : geqo.core.quantum_operation.QuantumOperation
            The operation that should be applied.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided operation.
        """
        # If there is a decomposition into a sequence of other gates, then use it.
        if gate.hasDecomposition() is True:
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            if dec is not None:
                for x in range(len(dec.qubits)):
                    qubitMapping[dec.qubits[x]] = targets[x]

                for d in dec.gatesAndTargets:
                    # self.apply(d[0], [qubitMapping[x] for x in d[1]])
                    key_type = type(dec.qubits[0])
                    apply_targets = [
                        qubitMapping[x]
                        if type(x) is key_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                    self.apply(d[0], apply_targets)

        elif gate.isUnitary():
            targetOrder = [q for q in targets]
            for q in list(range(self.numberQubits)):
                if q not in targetOrder:
                    targetOrder.append(q)

            perm = permutationMatrixQubitsSymPy(
                [targetOrder.index(q) for q in list(range(self.numberQubits))]
            )

            u = getUnitarySymPy(gate, self.values)
            u2 = TensorProduct(u, sym.eye(2 ** (self.numberQubits - len(targets))))
            u3 = perm.T * u2 * perm

            self.u = u3 * self.u
        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )


class newSimulatorUnitarySymPy(simulatorUnitarySymPy):
    """
    Calculate the unitary matrix corresponding to a sequence of
    gates. No non-unitary operations like ClassicalControl, Measurement
    or DropQubits are allowed.
    """

    def __init__(self, numberQubits: int):
        """
        The constructor of this simulator takes as parameters the number of qubits.

        Parameters
        ----------
        numberQubits : int
            The number of qubits of the simulated system.

        Returns
        -------
        newSimulatorUnitarySymPy : geqo.simulators.sympy.newSimulatorUnitarySymPy
            A simulator object, which is based on SymPy.
        """
        super().__init__(numberQubits)

    def prepareBackend(self, operations: list[QuantumOperation]):
        """
        For a list of supported operators, this method sets the necessary values for the simulator.

        Parameters
        ----------
        operations : list(geqo.core.quantum_operation.QuantumOperation)
            A list of quantum operations, for which the backend should be prepared.
        """
        for ops in operations:
            if isinstance(ops, QFT):
                logger.info("prepare execution of QFT")
                n = ops.numberQubits
                for j in range(1, n):
                    self.values[ops.nameSpacePrefix + "Ph" + str(j)] = (
                        2 * S.Pi / (2 ** (j + 1))
                    )
            elif isinstance(ops, InverseQFT):
                self.prepareBackend([ops.qft])
            elif isinstance(ops, PCCM):
                logger.info("prepare execution of PCCM")
                self.values[ops.nameSpacePrefix + "RX(π/2)"] = (
                    S.Pi / 2
                )  # getRX(S.Pi / 2)
                self.values[ops.nameSpacePrefix + "RX(-π/2)"] = (
                    -S.Pi / 2
                )  # getRX(-S.Pi / 2)
                self.values[ops.nameSpacePrefix + "RY(-π/2)"] = (
                    -S.Pi / 2
                )  # getRY(-S.Pi / 2)
                nameAngle = ops.nameSpacePrefix + ops.name
                if nameAngle not in self.values:
                    phi = sym.Symbol(nameAngle)
                    self.values[ops.nameSpacePrefix + "RX(" + str(phi) + ")"] = (
                        phi  # getRX(
                    )
                    # )
                # phi
                else:
                    logger.debug(
                        "found nameAngle %s with value %s ",
                        nameAngle,
                        self.values[nameAngle],
                    )
                    phi = sym.Symbol(nameAngle)
                    self.values[ops.nameSpacePrefix + "RX(" + str(phi) + ")"] = (
                        self.values[nameAngle]
                    )  # getRX(
                    # self.values[nameAngle]
                    # )
            elif isinstance(ops, InversePCCM):
                self.prepareBackend([ops.pccm])
            elif isinstance(ops, Toffoli):
                logger.info("prepare execution of Toffoli")
                self.values[ops.nameSpacePrefix + "S.Pi/4"] = S.Pi / 4
                self.values[ops.nameSpacePrefix + "-S.Pi/4"] = -S.Pi / 4
            else:
                raise Exception("operation not supported:", str(ops))

    def apply(self, gate: QuantumOperation, targets: list[int]):
        """
        Apply an operation to the quantum state, which is currently kept in the simulator.

        Parameters
        ----------
        gate : geqo.core.quantum_operation.QuantumOperation
            The operation that should be applied.
        targets : list(int)
            The list of qubit indexes, which are the target of the provided operation.
        """
        # If there is a decomposition into a sequence of other gates, then use it.
        if gate.hasDecomposition() is True:
            dec = gate.getEquivalentSequence()
            qubitMapping = {}
            if dec is not None:
                for x in range(len(dec.qubits)):
                    qubitMapping[dec.qubits[x]] = targets[x]

                for d in dec.gatesAndTargets:
                    # self.apply(d[0], [qubitMapping[x] for x in d[1]])
                    key_type = type(dec.qubits[0])
                    apply_targets = [
                        qubitMapping[x]
                        if type(x) is key_type
                        else qubitMapping[dec.qubits[x]]
                        for x in d[1]
                    ]
                    self.apply(d[0], apply_targets)

        elif gate.isUnitary():
            u = getUnitarySymPy(gate, self.values)
            u_perm = multiQubitsUnitary(u, [*range(self.numberQubits)], targets)

            self.u = u_perm * self.u
        else:
            logger.error(
                "gate not implemented for %s: %s", self.__class__.__name__, gate
            )
            raise Exception(
                f"gate not implemented for {self.__class__.__name__}: {gate}"
            )
