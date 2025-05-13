import pytest
import numpy as np
from Src.Models.Circuit import Circuit
from Src.Models.Network import Network
from Src.Models.Component import (
    R, L, C, G, Attenuator, Isolator, Splitter, Coupler,
    Port, Ground, Open
)

@pytest.fixture
def base_params():
    """Base parameters for testing"""
    return {
        'frequency': np.array([1e9, 2e9, 3e9]),
        'z0': 50.0+0j
    }

@pytest.fixture
def sample_networks():
    """Sample circuit with two networks"""
    networks = {
        'ntw1': Network(
            frequency=np.array([1e9, 2e9, 3e9]),
            s_parameters=np.array([
                [[0.1+0.2j]],
                [[0.2+0.3j]],
                [[0.3+0.4j]]
            ]),
            z0=50.0+0j,
            nports=1
        ),
        'ntw2': Network(
            frequency=np.array([1e9, 2e9, 3e9]),
            s_parameters=np.array([
                [[0.4+0.5j]],
                [[0.5+0.6j]],
                [[0.6+0.7j]]
            ]),
            z0=50.0+0j,
            nports=1
        )
    }
    return Circuit(
        networks=networks,
        connections=[[('ntw1', 0), ('ntw2', 0)]]
    )

@pytest.fixture
def rlgc_circuit(base_params):
    """Create a circuit with RLGC components"""
    return Circuit(
        networks={
            'r1': R(r=50, **base_params),
            'l1': L(l=1e-9, **base_params),
            'c1': C(c=1e-12, **base_params),
            'g1': G(g=0.01, **base_params)
        },
        connections=[
            [('r1', 0), ('l1', 0), ('c1', 1)],
            [('c1', 0), ('g1', 0), ('r1', 1)],
            [('g1', 1), ('l1', 1)]
        ]
    )

@pytest.fixture
def microwave_circuit(base_params):
    """Create a circuit with microwave components"""
    return Circuit(
        networks={
            'att1': Attenuator(s21=3, db=True, **base_params),
            'iso1': Isolator(source_port=0, **base_params),
            'spl1': Splitter(nports=3, **base_params),
            'cpl1': Coupler(db=3, deg=90, **base_params)
        },
        connections=[
            [('att1', 0), ('iso1', 0), ('spl1', 1)],
            [('spl1', 0), ('cpl1', 0)]
        ]
    )

@pytest.fixture
def sim_circuit(base_params):
    """Create a circuit with simulation components"""
    return Circuit(
        networks={
            'port1': Port(name="port1", **base_params),
            'ground1': Ground(name="ground1", **base_params),
            'open1': Open(name="open1", **base_params)
        },
        connections=[
            [('port1', 0), ('ground1', 0)],
            [('open1', 0)]
        ]
    )

class TestCircuit:
    def test_circuit_conversion(self, sample_networks):
        """Test basic network circuit conversion"""
        # Test initial circuit
        assert len(sample_networks.networks) == 2
        assert len(sample_networks.connections[0]) == 2

        # Convert to scikit-rf circuit
        rf_circuit = sample_networks.to_circuit()
        assert len(rf_circuit.networks_dict()) == 2
        
        # Convert back and verify
        circuit = Circuit.from_circuit(rf_circuit)
        assert len(circuit.networks) == 2
        assert len(circuit.connections[0]) == 2

    def test_rlgc_circuit(self, rlgc_circuit):
        """Test circuit with RLGC components"""
        # Convert to scikit-rf circuit
        rf_circuit = rlgc_circuit.to_circuit()
        
        # Verify network count and names
        assert len(rf_circuit.networks_dict()) == 4
        network_names = list(rf_circuit.networks_dict().keys())
        assert all(name in network_names for name in ['r1', 'l1', 'c1', 'g1'])
        
        # Verify all networks have expected shape
        for net in rf_circuit.networks_dict().values():
            assert net.s.shape == (3, 2, 2)
        
        # Verify connections
        assert len(rf_circuit.connections) == 3
        
    def test_microwave_circuit(self, microwave_circuit):
        """Test circuit with microwave components"""
        # Convert to scikit-rf circuit
        rf_circuit = microwave_circuit.to_circuit()
        
        # Verify network count
        assert len(rf_circuit.networks_dict()) == 4
        
        # Verify network types
        network_names = list(rf_circuit.networks_dict().keys())
        assert all(name in network_names for name in ['att1', 'iso1', 'spl1', 'cpl1'])
        
        # Verify connections
        assert len(rf_circuit.connections) == 2

    def test_frequency_validation(self, base_params):
        """Test frequency validation"""
        # Create circuit with mismatched frequencies
        r1 = R(r=50, **base_params)
        r2 = R(r=100, frequency=[2e9, 2.1e9, 2.2e9], z0=base_params['z0'])
        
        with pytest.raises(ValueError):
            Circuit(
                networks={'r1': r1, 'r2': r2},
                connections=[[('r1', 0), ('r2', 0)]]
            )

    def test_connection_validation(self, base_params):
        """Test connection validation"""
        # Create circuit with invalid connection
        with pytest.raises(ValueError):
            Circuit(
                networks={'r1': R(r=50, **base_params)},
                connections=[[('r1', 0), ('invalid_network', 0)]]
            )

    def test_sim_circuit(self, base_params):
        """Test circuit with simulation components (Port, Ground, Open)"""
        # Create circuit with simulation components
        sim_circuit = Circuit(
            networks={
                'port1': Port(name="port1", **base_params),
                'ground1': Ground(name="ground1", **base_params),
                'open1': Open(name="open1", **base_params),
                'port2': Port(name="port2", **base_params),
            },
            connections=[[('port1', 0), ('ground1', 0)],
                        [('open1', 0)], [('port2', 0)]]
        )

        # Convert to scikit-rf circuit
        rf_circuit = sim_circuit.to_circuit()
        
        # Verify network count
        assert len(rf_circuit.networks_dict()) == 4
        
        # Verify network types and attributes
        for name, net in rf_circuit.networks_dict().items():
            if name == 'port1' or name == 'port2':
                assert net._is_circuit_port is True
                assert net.s.shape == (3, 1, 1)
            elif name == 'ground1':
                assert net.s.shape == (3, 2, 2)
            elif name == 'open1':
                assert net.s.shape == (3, 2, 2)

    def test_mixed_component_types(self, base_params):
        """Test circuit with mixed component types (RLGC, Microwave, SimComponent)"""
        circuit = Circuit(
            networks={
                'r1': R(r=50, **base_params),
                'port1': Port(name="port1", **base_params),
                'ground1': Ground(name="ground1", **base_params),
                'att1': Attenuator(s21=3, db=True, **base_params)
            },
            connections=[
                [('port1', 0), ('r1', 0)],
                [('r1', 1), ('att1', 0)],
                [('att1', 1), ('ground1', 0)]
            ]
        )
        
        # Convert to scikit-rf circuit
        rf_circuit = circuit.to_circuit()
        
        # Verify network count and types
        assert len(rf_circuit.networks_dict()) == 4
        network_names = list(rf_circuit.networks_dict().keys())
        assert all(name in network_names for name in ['r1', 'port1', 'ground1', 'att1'])
        
        # Verify network shapes
        for name, net in rf_circuit.networks_dict().items():
            if name == 'port1':
                assert net.s.shape[1:] == (1, 1)  # 1-port
            else:
                assert net.s.shape[1:] == (2, 2)  # 2-port
        
        # Verify connections form a valid chain
        assert len(rf_circuit.connections) == 3
        conn_pairs = {
            ('port1', 'r1'),
            ('r1', 'att1'),
            ('att1', 'ground1')
        }
        for conn in rf_circuit.connections:
            pair = tuple(sorted([c[0].name for c in conn]))
            assert pair in {tuple(sorted(p)) for p in conn_pairs}

if __name__ == "__main__":
    test = TestCircuit()
    sample = sample_networks()
    test.test_circuit_conversion(sample)