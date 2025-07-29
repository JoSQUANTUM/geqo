import sympy as sym
from sympy.physics.quantum import TensorProduct
import itertools
from geqo.utils._base_.helpers import bin2num, num2bin
from typing import Any


def permutationMatrixQubitsSymPy(perm: list[int]) -> sym.Matrix:
    """
    Return a permutation matrix for given qubit permutation.

    Params
    ------
        perm: list[int]
            The permutation of qubits in list form. Each entry is the index after the permutation.

    Results
    -------
        sym.Matrix
            The permutation matrix corresponding to the provided permutation of qubits.
    """
    permMat = sym.zeros(len(perm), len(perm))
    for i in range(len(perm)):
        permMat[perm[i], i] = 1
    res = sym.zeros(2 ** len(perm), 2 ** len(perm))
    for t in itertools.product([0, 1], repeat=len(perm)):
        v = sym.Matrix(t)
        b = permMat * v
        r = [b[i] for i in range(len(perm))]
        res[bin2num(list(r)), bin2num(list(t))] = 1
    return res


def getSingleQubitOperationOnRegister(
    u: sym.Matrix, numberQubits: int, targets: list[int]
) -> sym.Matrix:
    """
    Apply a single-qubit operation to specific qubits in register. This generates a unitary matrix for the full
    system.

    Params
    ------
        u: sym.Matrix
            The unitary matrix that should be applied to the whole system.
        numberQubits: int
            The number of qubits of the whole quantum register.
        targets: list[int]
            A list of indexes, on which the given unitary operator should work.

    Results
    -------
        sym.Matrix
            The unitary matrix corresponding to the operation on the target qubits.

    """
    targetOrder = [q for q in targets]
    for q in range(numberQubits):
        if q not in targetOrder:
            targetOrder.append(q)
    perm = permutationMatrixQubitsSymPy(
        [targetOrder.index(q) for q in range(numberQubits)]
    )
    u2 = TensorProduct(u, sym.eye(2 ** (numberQubits - len(targets))))
    return perm.T * u2 * perm


def partialTrace(
    rho: sym.Matrix, qubits: list[int], dropTargets: list[int]
) -> tuple[sym.Matrix, sym.Matrix]:
    """Compute partial trace of density matrix."""
    undroppedQubits = [q for q in qubits if q not in dropTargets]
    targetOrder2 = undroppedQubits + dropTargets
    perm = permutationMatrixQubitsSymPy([targetOrder2.index(q) for q in qubits])
    rho2 = perm * rho * perm.T
    newNumberQubits = len(qubits) - len(dropTargets)

    newEntries: dict[tuple[Any, Any], sym.Matrix] = {}
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

    rhoNew = sym.zeros(2**newNumberQubits, 2**newNumberQubits)
    for n in newEntries:
        rhoNew[n[0], n[1]] = newEntries[n]
    return rhoNew, perm


def projection(densityMatrix, num_qubits, targets, basis):
    """Construct the projector of a given basis state and compute the projected density matrix."""
    zero = sym.Matrix([1, 0])
    one = sym.Matrix([0, 1])
    identity = sym.Matrix([1, 1])

    # construct the projector
    matrices = []
    for i in range(num_qubits):
        if i in targets:
            component = zero if basis[sorted(targets).index(i)] == 0 else one
            matrices.append(component)
        else:
            matrices.append(identity)

    proj = TensorProduct(*matrices)

    # projector applied to the density matrix
    nonzero = [i for i, x in enumerate(proj) if x != 0]
    nonzero_pair = list(itertools.combinations(nonzero, 2))
    resultRho = sym.zeros(2**num_qubits, 2**num_qubits)
    for i in nonzero:
        resultRho[i, i] = densityMatrix[i, i]
    for i, j in nonzero_pair:
        resultRho[i, j] = densityMatrix[i, j]
        resultRho[j, i] = densityMatrix[j, i]

    return resultRho


def multiQubitsUnitary(u, qubits, targets):
    """Construct multi-qubit unitary matrix without permuting the qubits"""
    target_idx = [qubits.index(t) for t in targets]
    non_target_idx = [qubits.index(i) for i in qubits if i not in targets]
    num_qubits = len(qubits)
    U = sym.zeros(2**num_qubits, 2**num_qubits)

    for Ti in range(2 ** len(targets)):  # targets binary value
        for Tj in range(Ti, 2 ** len(targets)):
            binTi = num2bin(Ti, len(targets))  # binary representation. i.e. 2 = (1,0)
            sorted_binTi = [
                binTi[sorted(target_idx).index(t)] for t in target_idx
            ]  # if targets are [q2,q0] then permute the order such that q2 matches the first bit
            binTj = num2bin(Tj, len(targets))
            sorted_binTj = [binTj[sorted(target_idx).index(t)] for t in target_idx]

            for N in range(2 ** len(non_target_idx)):  # non targets binary value
                binN = num2bin(N, len(non_target_idx))

                Ui = sum(
                    binTi[i] * 2 ** (len(qubits) - 1 - sorted(target_idx)[i])
                    for i in range(len(targets))
                )
                Uj = sum(
                    binTj[i] * 2 ** (len(qubits) - 1 - sorted(target_idx)[i])
                    for i in range(len(targets))
                )

                Nindex = sum(
                    binN[i] * 2 ** (len(qubits) - 1 - non_target_idx[i])
                    for i in range(len(non_target_idx))
                )

                Ui += Nindex
                Uj += Nindex

                ui, uj = bin2num(sorted_binTi), bin2num(sorted_binTj)
                U[Ui, Uj] = u[ui, uj]
                U[Uj, Ui] = u[uj, ui]

    return U


def newPartialTrace(rho, qubits, dropTargets):
    """Compute partial trace of density matrix faster."""
    dropindex = sorted([qubits.index(i) for i in dropTargets])
    keepindex = [x for x in list(range(len(qubits))) if x not in dropindex]

    reduced = sym.zeros(2 ** len(keepindex), 2 ** len(keepindex))
    for ti in range(2 ** len(keepindex)):
        for tj in range(ti, 2 ** len(keepindex)):
            binti = num2bin(ti, len(keepindex))
            bintj = num2bin(tj, len(keepindex))
            reducedIndexi = sum(
                binti[i] * 2 ** (len(qubits) - 1 - keepindex[i])
                for i in range(len(keepindex))
            )
            reducedIndexj = sum(
                bintj[i] * 2 ** (len(qubits) - 1 - keepindex[i])
                for i in range(len(keepindex))
            )
            value = 0
            for n in itertools.product([0, 1], repeat=len(dropindex)):
                dropdecimal = sum(
                    n[i] * 2 ** (len(qubits) - 1 - dropindex[i])
                    for i in range(len(dropindex))
                )
                value += rho[reducedIndexi + dropdecimal, reducedIndexj + dropdecimal]

            reduced[ti, tj] = value
            reduced[tj, ti] = sym.conjugate(value)

    return reduced
