import unittest
import pytest
from Src.Models.Circuit import Circuit
import skrf as rf


def sample_circuit():
    ntw1 = rf.Network(name='ntw1', s=[[0.1+0.2j]], f=[1e9], z0=50)
    ntw2 = rf.Network(name='ntw2', s=[[0.3+0.4j]], f=[1e9], z0=50)
    circuit = rf.Circuit(connections=[[(ntw1, 0), (ntw2, 0)]])
    circuit.networks_list = [ntw1, ntw2]  # Explicitly set networks_list
    return circuit

def test_circuit_conversion(sample_circuit):
    circuit = Circuit.from_circuit(sample_circuit)
    assert len(circuit.networks) == 2  # Correct attribute name
    assert len(circuit.connections[0]) == 2

    reconverted = circuit.to_circuit()
    assert len(reconverted.networks_list) == 2  # scikit-rf uses networks_list

if __name__ == "__main__":
    test_circuit_conversion(sample_circuit())