# geqo Documentation
geqo is a framework for constructing and describing quantum circuits and executing them on simulators and on quantum hardware devices.

## Quick installation and testing
- clone the repository: git clone [https://github.com/JoSQUANTUM/geqo](https://github.com/JoSQUANTUM/geqo)
- create a virtual environment: `python3 -m venv geqo-test`
- enable environment: `source geqo-test/bin/activate`
- install geqo with all options: `pip3 install -e geqo/[sympy,numpy,visualization,dev]`
- optional: run unit tests: `python -m pytest geqo/tests/`
- small example: start Python in the environment and get unitary of a quantum circuit for the EPR pair generation:
```
from geqo.gates import Hadamard, CNOT
from geqo.core import Sequence
seq=Sequence([],["q1","q2"],[ (Hadamard(),["q1"]), (CNOT(), ["q1","q2"]) ])

from geqo.simulators import newSimulatorUnitarySymPy
sim=newSimulatorUnitarySymPy(2)
sim.apply(seq,[0,1])
sim.u
```

## Why a new framework for quantum circuits?
Quantum circuits serve as a general model for quantum computations, employing abstract concepts like bit flips or rotations with
specific angles on qubits.

In practical applications, circuits are executed on a variety of backends, including different numerical or symbolic simulators, as well as various quantum hardware systems. Each of these backends typically has a unique method for representing a given operation
and its parameters.

Consequently, it is desirable to encode quantum circuits using an abstract, representation-independent language. This is precisely the function of geqo. The separation between the circuit description and the concrete backend representation minimizes dependencies on other software packages, keeps geqo lightweight and facilitates easy extension and customization.

## Features
* Quantum circuit construction (e.g. basic gates, controlled gates, measurements, classical and quantum control)
* simulators for numerical and symbolic evaluation of circuits, density matrices, state vectors, measurement results
* converter for OpenQASM3
* based on Python with a minimum set of dependencies
* extendible and customizable

## Installation
Instructions for the installation of geqo can be found [here](installation.md)

## Getting started
An overview of the features of geqo for constructing and simulating quantum circuits can be found in the [Introduction](notebooks/Introduction0.ipynb) section.

## API reference
The API has an extensive documentation. Start [here](api-reference.md) to dive into the geqo API.

## Support and contribution
Please contact us under the email address support@jos-quantum.de
