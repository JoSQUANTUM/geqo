# Tutorials

The notebooks in this section contain further information and examples on the following specific topics.

- **Name Space Prefixes**: Some pre-defined gates in geqo are internally composed of several other gates, which might have parameters. To avoid naming conflicts, a name space prefix can be provided to the relevant gate constructors in order to avoid double-using names.
- **Calculation of the Partial Trace**: The partial trace is used to calculate the resulting density matrix of a system if one or more qubits are dropped.
- **Example for Quantum-Amplitude-Estimation**: The Quantum Amplitude Estimation is applied to a simple example circuit and the probability of a measurement result is estimated with 4 bits of precesion.
- **Quantum Amplitude Estimation of risk models**: A quantum version of a business risk model is constructed and the Quantum Amplitude Estimation is used to estimate the probability of an event in the model.
- **Decomposition of gates with many controls**: Many hardware implementations of quantum computers have basic gates, which act on a small number of qubits only. To execute gates with a high number of control qubits, a decomposition is necessary. In this notebook, the decomposition of a highly controlled ```PauliX``` gate into Toffoli gates is studied.
