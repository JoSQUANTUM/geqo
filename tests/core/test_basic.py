from geqo.core.basic import BasicGate, InverseBasicGate


class TestBasic:
    def test_basic_gate(self):
        name = "bg"
        num_qubits = 1
        op = BasicGate(name, num_qubits)

        assert op.name == name
        assert op.numberQubits == num_qubits
        assert str(op) == 'BasicGate("' + name + '", ' + str(num_qubits) + ")"
        assert op == BasicGate(name, num_qubits)
        assert not op == InverseBasicGate(name, num_qubits)
        assert op.getInverse() == InverseBasicGate(name, num_qubits)
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()

    def test_inverse_basic_gate(self):
        name = "ig"
        num_qubits = 1
        op = InverseBasicGate(name, num_qubits)

        assert op.name == name
        assert op.numberQubits == num_qubits
        assert str(op) == 'InverseBasicGate("' + name + '", ' + str(num_qubits) + ")"
        assert op == InverseBasicGate(name, num_qubits)
        assert not op == BasicGate(name, num_qubits)
        assert op.getInverse() == BasicGate(name, num_qubits)
        assert op.getEquivalentSequence() is None
        assert op.getNumberQubits() == 1
        assert op.getNumberClassicalBits() == 0
        assert not op.hasDecomposition()
        assert op.isUnitary()
