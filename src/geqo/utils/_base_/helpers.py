from geqo.core import Sequence
from geqo.operations.measurement import Measure
import itertools


def bin2num(c):
    """
    Convert binary list to decimal number.

    Parameters
    ----------
    c : list([0|1])
        A list of 0 and 1 values.

    Returns
    -------
     result : int
        The integer value corresponding to the binary list.

    """
    if len(c) == 0:
        return 0
    elif c[-1] == 0:
        return 2 * bin2num(c[:-1])
    else:
        return 2 * bin2num(c[:-1]) + 1


def num2bin(num, digits):
    """
    Convert a decimal number to a binary representation in list form.

    Parameters
    ----------
    num : int
        An integer.

    Returns
    -------
     btstr : list([0|1])
        A list of 0 and 1, which is the binary representation of the given number.
    """
    bstr = bin(num)[2:].zfill(digits)
    return [int(b) for b in bstr]


def permutationMatrixQubits(perm):
    """
    Return permutation matrix for given qubit permutation.

    This function is the fallback function if no suitable framework (like NumPy or SymPy) is installed for this function.
    """
    raise NotImplementedError("""
                        Base function requires at least one optional feature.
                        Run pip install geqo[numpy] or pip install geqo[sympy]
                        """)


def getSingleQubitOperationOnRegister(u, numberQubits, targets):
    """
    Apply single-qubit operation to specific qubits in register.

    This function is the fallback function if no suitable framework (like NumPy or SymPy) is installed for this function.
    """
    raise NotImplementedError("""
                        Base function requires at least one optional feature.
                        Run pip install geqo[numpy] or pip install geqo[sympy]
                        """)


def partialTrace(rho, qubits, dropTargets):
    """
    Compute partial trace of density matrix.

    This function is the fallback function if no suitable framework (like NumPy or SymPy) is installed for this function.
    """
    raise NotImplementedError("""
                        Base function requires at least one optional feature.
                        Run pip install geqo[numpy] or pip install geqo[sympy]
                        """)


def embedSequences(seq):
    """
    This function scans through the operations in a ```Sequence``` object and replaces all occurences of ```Sequence``` objects in it by the corresponding operations in it.
    This function only replaces ```Sequence``` objects on the first level, i.e. it does not replace recursively all ```Sequence``` objects within other ```Sequence``` objects.

    Parameters
    ----------
    seq : geqo.core.quantum_circuit.Sequence
        A ```Sequence``` object.

    Returns
    -------
    res : geqo.core.quantum_circuit.Sequence
        A ```Sequence``` object with all `occurences of ``Sequence``` objects on the first level replaced by the corresponding operators.

    """
    res = []
    for operation in seq.gatesAndTargets:
        gate = operation[0]
        targets = operation[1]
        if isinstance(gate, Sequence):
            # if targets of the subsequence are integers and gate.qubits are strings, convert gate.qubits to integers
            """qubits = (
                [*range(len(gate.qubits))]
                if type(gate.gatesAndTargets[0][1][0]) is int
                else gate.qubits
            )
            bits = (
                [*range(len(gate.bits))]
                if type(gate.gatesAndTargets[0][1][0]) is int
                else gate.bits
            )"""
            qubits = gate.qubits
            bits = gate.bits

            qubitMapping = {q: targets[i] for i, q in enumerate(qubits)}
            seq_qubits = [*range(len(seq.qubits))]
            seq_bits = [*range(len(seq.bits))]
            bitMapping = {
                bits[i]: seq_bits[seq_qubits.index(qubitMapping[qubits[i]])]
                for i in range(len(bits))
            }
            for s_operation in gate.gatesAndTargets:
                s_gate = s_operation[0]
                s_targets = s_operation[1]
                if isinstance(s_gate, Measure):
                    qkey_type = type(qubits[0])
                    apply_qtargets = [
                        qubitMapping[x]
                        if type(x) is qkey_type
                        else qubitMapping[qubits[x]]
                        for x in s_targets
                    ]
                    ckey_type = type(bits[0])
                    apply_ctargets = [
                        bitMapping[x] if type(x) is ckey_type else bitMapping[bits[x]]
                        for x in s_operation[2]
                    ]
                    res.append(
                        (
                            s_gate,
                            apply_qtargets,
                            apply_ctargets,
                        )
                    )
                    """res.append(
                        (
                            s_gate,
                            [qubitMapping[x] for x in s_targets],
                            [bitMapping[x] for x in s_operation[2]],
                        )
                    )"""
                else:
                    qkey_type = type(qubits[0])
                    apply_qtargets = [
                        qubitMapping[x]
                        if type(x) is qkey_type
                        else qubitMapping[qubits[x]]
                        for x in s_targets
                    ]
                    res.append((s_gate, apply_qtargets))
                    # res.append((s_gate, [qubitMapping[x] for x in s_targets]))
        else:
            if isinstance(gate, Measure):
                res.append((gate, targets, operation[2]))
            else:
                res.append((gate, targets))
    return Sequence(seq.bits, seq.qubits, res, name=seq.name)


def partial_diag(rho, qubits, dropTargets):
    """
    Compute the partial trace (trace out the dropTargets) and extract the non-zero diagonal element of the reduced density matrix.

    Parameters
    ----------
    rho : numpy.ndarry | sympy.Matrix
        A density matrix.
    qubits : list(int|String)
        A list of qubits of a register.
    dropTargets : list(int|String)
        The qubits that are discarded.

    Returns
    -------
    nonzero : list((list([0|1]), numpy.float64 | sympy.core ))
        A list of pairs. The first component of a pair is a binary representation of the index of a diagonal element of the density matrix. The second component is the corresponding entry.

    """
    dropindex = sorted([qubits.index(i) for i in dropTargets])
    keepindex = [x for x in list(range(len(qubits))) if x not in dropindex]

    nonzero = []
    for t in itertools.product([0, 1], repeat=len(keepindex)):
        keep = sum(
            t[i] * 2 ** (len(qubits) - 1 - keepindex[i]) for i in range(len(keepindex))
        )
        prob = 0
        for n in itertools.product([0, 1], repeat=len(dropindex)):
            index = keep + sum(
                n[i] * 2 ** (len(qubits) - 1 - dropindex[i])
                for i in range(len(dropindex))
            )
            prob += rho[index, index]

        if prob != 0:
            nonzero.append((t, prob))
    return nonzero
