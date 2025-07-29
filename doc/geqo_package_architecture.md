# geqo Quantum Framework Package Architecture
The following overviews show the structure of the geqo source code.

## Package Structure Overview
The main file tree of geqo is shown in the following diagram.

```
geqo/
├── __init__.py
├── algorithms/
│   ├── __init__.py
│   ├── algorithms.py
│   └── risk_model.py
├── core/
│   ├── __init__.py
│   ├── basic.py
│   ├── quantum_circuit.py
│   └── quantum_operation.py
├── gates/
│   ├── __init__.py
│   ├── fundamental_gates.py
│   ├── multi_qubit_gates.py
│   └── rotation_gates.py
├── initialization/
│   ├── __init__.py
│   └── state.py
├── operations/
│   ├── __init__.py
│   ├── controls.py
│   └── measurement.py
├── simulators/
│   ├── __init__.py
│   ├── base.py
│   ├── numpy/
│   │   ├── __init__.py
│   │   └── implementation.py
│   └── scipy/
│       ├── __init__.py
│       └── implementation.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── visualization/
│   ├── __init__.py
│   ├── common.py
│   ├── latex.py
│   └── mpl.py
└── tests/
    ├── __init__.py
    ├── test_core.py
    ├── test_algorithms.py
    └── ...
```

## Module Responsibilities
The location of the main class definitions, which are used for defining quantum operations and circuits, can be found in
the following list:

- `core/quantum_operation.py`:
    - QuantumOperation: The abstract base class for all quantum operations

- `core/quantum_circuit.py`:
    - Sequence: The class for lists of operations corresponding to quantum circuits.

- `gates/basic.py`:
    - BasicGate, InverseBasicGate: The class for defining arbitrary unitary gates and its inverses.

- `gates/multi_qubit_gates.py`
    - Toffoli: The class for a Pauli X operation, which is controlled by two qubits.

- `gates/fundamental_gates.py`
    - PauliX, PauliY, PauliZ: The classes for unitary Pauli operations on a qubit.
    - Hadamard: The class for a Hadamard transform on a qubit.
    - Phase, InversePhase: The class for a phase operation on a qubit ant the inverse phase operation.
    - CNOT: The class for a PauliX operation on a qubit, which is controlled by another qubit.
    - SwapQubits: The class for exchanging two qubits.
    - SGate, InverseSGate: The class for the square root of the Pauli Z operation.

- `gates/rotation_gates.py`
    - Rx, Ry, Rz, InverseRx, InverseRy, InverseRz: The classes for rotations in the Bloch sphere and their inversees.
    - Rzz, InverseRzz: The class for a rotation on two qubits.

- `operations/controls.py`: Controlled operations (QuantumControl, ClassicalControl)
    - ClassicalControl: Class for defining gates, which are controlled by classical bits.
    - QuantumControl: Class for defining gates, which are controlled by qubits.

- `operations/measurement.py:`
    - Measure: Class for defining a measurement of qubits and writing the results to classical bits.
    - DropQubits: Class for tracing out one or more qubits.

- `initialization/state.py`:
    - SetBits: Class for setting the values of classical bits.
    - SetQubits: Class for setting one of the computational basis states of a qubit.
    - SetDensityMatrix: Class for setting the density matrix of one or more qubits.


