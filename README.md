# geqo
geqo is a framework for constructing and describing quantum circuits and executing them on simulators and on quantum hardware devices.

The documentation can be found [here](doc/intro.md).

## Quick installation and testing
- clone the repository: git clone [https://github.com/JoSQUANTUM/geqo](https://github.com/JoSQUANTUM/geqo)
- create a virtual environment: `python -m venv geqo-env`
- enable environment: `source geqo-env/bin/activate`
- install geqo with all options: `pip install geqo[sympy,numpy,visualization,dev]`
- optional: run unit tests: `python -m pytest geqo/tests/`

## Running a simple example
- the example task is to get unitary of a quantum circuit for the EPR pair generation
- start Python in the environment from the steps above
- run the following commands:

```
from geqo.gates import Hadamard, CNOT
from geqo.core import Sequence
seq=Sequence([],["q1","q2"],[ (Hadamard(),["q1"]), (CNOT(), ["q1","q2"]) ])

from geqo.simulators import newSimulatorUnitarySymPy
sim=newSimulatorUnitarySymPy(2)
sim.apply(seq,[0,1])
sim.u
```

The expected result is
```
Matrix([
[sqrt(2)/2,         0,  sqrt(2)/2,          0],
[        0, sqrt(2)/2,          0,  sqrt(2)/2],
[        0, sqrt(2)/2,          0, -sqrt(2)/2],
[sqrt(2)/2,         0, -sqrt(2)/2,          0]])
```

