import unittest
from models.Circuit import Circuit
import skrf as rf

class TestCircuit(unittest.TestCase):
    def test_circuit_creation_from_skrf(self):
        # Create example circuit manually or use existing skrf data
        connections = [[('', 0), ('', 0)]]
        circuit = rf.Circuit(connections)
        circuit_schema = Circuit.from_circuit(circuit)
        self.assertIsInstance(circuit_schema, Circuit)

    def test_circuit_to_skrf_conversion(self):
        # Make a circuit schema, convert back to skrf circuit
        connections = [[('', 0), ('', 0)]]
        cir = rf.Circuit(connections)
        circuit_schema = Circuit.from_circuit(cir)
        new_circuit = circuit_schema.to_circuit()
        self.assertEqual(cir.connections, new_circuit.connections)

if __name__ == '__main__':
    unittest.main()