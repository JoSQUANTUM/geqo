import numpy as np
from numpy.typing import NDArray
import itertools
from typing import Any
from geqo.utils._base_.helpers import bin2num


def permutationMatrixQubitsNumPy(perm: list[int]) -> NDArray:
    """
    Return permutation matrix for given qubit permutation.

    Parameters
    ----------
        perm : list[int]
            The permutation of qubits in list form. The elements are indexed starting with 0. For instance,
            [0,2,1] denotes the permutation of 3 qubits, where the last 2 qubits are flipped.

    Returns
    -------
        NDArray
            A permutation matrix on the state space of the qubits. The matrix corresponds to the
            permutation of the qubits.
    """
    permMat = np.zeros((len(perm), len(perm)))
    for i in range(len(perm)):
        permMat[perm[i], i] = 1
    res = np.zeros((2 ** len(perm), 2 ** len(perm)))
    for t in itertools.product([0, 1], repeat=len(perm)):
        v = np.array(t).reshape(len(perm), 1)
        b = permMat @ v
        r = [b[i] for i in range(len(perm))]
        res[bin2num(list(r)), bin2num(list(t))] = 1
    return res


def getSingleQubitOperationOnRegister(
    u: NDArray, numberQubits: int, targets: list[int]
) -> NDArray:
    """
    Apply single-qubit operation to specific qubits in register. This function embeds the given matrix into
    the matrix corresponding to the whole system.

    Parameters
    ----------
        u : NDArray
            The unitary matrix, which is applied to a part of the whole quantum register.
        numberQubits: int
            The size of the quantum register.
        targets: list[int]
            The list of qubits, on which the operation is applied to.

    Returns
    -------
        NDArray
            A matrix on the whole register, which is the embedding of the provided operation.
    """
    targetOrder = [q for q in targets]
    for q in range(numberQubits):
        if q not in targetOrder:
            targetOrder.append(q)
    perm = permutationMatrixQubitsNumPy(
        [targetOrder.index(q) for q in range(numberQubits)]
    )
    u2 = np.kron(u, np.eye(2 ** (numberQubits - len(targets))))
    return perm.T * u2 * perm


def partialTrace(
    rho: NDArray, qubits: list[int], dropTargets: list[int]
) -> tuple[NDArray, NDArray]:
    """
    Compute the partial trace of a density matrix. The density matrix is reduced to the
    remaining qubits. The new density matrix is obtained by tracing out the dropped qubit.
    In general, this leads to mixed states.

    Parameters
    ----------
        rho: NDArray
            The density matrix before dropping qubits.
        qubits: list[int]
            The list of all qubits of a quantum register.
        dropTargets: list[int]
            The list of qubits, which are dropped.

    Returns
    -------
        tuple[NDArray, NDArray]
            The first result matrix is the reduced density matrix. The second result
            matrix is the permutation matrix, which moves the remaining entries of the
            original density matrix to the front.
    """
    undroppedQubits = [q for q in qubits if q not in dropTargets]
    targetOrder2 = undroppedQubits + dropTargets
    perm = permutationMatrixQubitsNumPy([targetOrder2.index(q) for q in qubits])
    rho2 = perm * rho * perm.T
    newNumberQubits = len(qubits) - len(dropTargets)

    newEntries: dict[tuple[Any, Any], NDArray] = {}
    for t1 in itertools.product([0, 1], repeat=newNumberQubits):
        for t2 in itertools.product([0, 1], repeat=newNumberQubits):
            newIndex1 = bin2num(t1)
            newIndex2 = bin2num(t2)
            for t3 in itertools.product([0, 1], repeat=len(qubits) - newNumberQubits):
                oldIndex1 = bin2num(t1 + t3)
                oldIndex2 = bin2num(t2 + t3)
                if (newIndex1, newIndex2) in newEntries:
                    newEntries[(newIndex1, newIndex2)] += rho2[(oldIndex1, oldIndex2)]
                else:
                    newEntries[(newIndex1, newIndex2)] = rho2[(oldIndex1, oldIndex2)]

    rhoNew = np.zeros(2**newNumberQubits, 2**newNumberQubits)
    for n in newEntries:
        rhoNew[n[0], n[1]] = newEntries[n]
    return rhoNew, perm
