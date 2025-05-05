import pytest
from Src.Models.Circuit import Circuit
from Src.Models.Component import (
    R, L, C, G, Attenuator, Isolator, Splitter, Coupler,
    Port, Ground, Open
)
import skrf as rf

@pytest.fixture
def base_params():
    """Common parameters for testing"""
    return {
        'frequency': [1e9, 1.1e9, 1.2e9],
        'z0': [[50.0, 0.0], [50.0, 0.0], [50.0, 0.0]]
    }

@pytest.fixture
def sample_circuit():
    """Create a simple two-port network circuit"""
    ntw1 = rf.Network(name='ntw1', s=[[0.1+0.2j]], f=[1e9], z0=50)
    ntw2 = rf.Network(name='ntw2', s=[[0.3+0.4j]], f=[1e9], z0=50)
    circuit = rf.Circuit(connections=[[(ntw1, 0), (ntw2, 0)]])
    circuit.networks_list = [ntw1, ntw2]
    return circuit

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
            [('r1', 0), ('l1', 0)],
            [('c1', 0), ('g1', 0)]
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
    def test_circuit_conversion(self, sample_circuit):
        """Test basic network circuit conversion"""
        circuit = Circuit.from_circuit(sample_circuit)
        assert len(circuit.networks) == 2
        assert len(circuit.connections[0]) == 2

        reconverted = circuit.to_circuit()
        assert len(reconverted.networks_list) == 2

    def test_rlgc_circuit(self, rlgc_circuit):
        """Test circuit with RLGC components"""
        # Convert to scikit-rf circuit
        rf_circuit = rlgc_circuit.to_circuit()
        
        # Verify network count
        assert len(rf_circuit.networks_list) == 4
        
        # Verify network types
        network_names = [ntw.name for ntw in rf_circuit.networks_list]
        assert all(name in network_names for name in ['r1', 'l1', 'c1', 'g1'])
        
        # Verify connections
        assert len(rf_circuit.connections) == 2
        
    def test_microwave_circuit(self, microwave_circuit):
        """Test circuit with microwave components"""
        # Convert to scikit-rf circuit
        rf_circuit = microwave_circuit.to_circuit()
        
        # Verify network count
        assert len(rf_circuit.networks_list) == 4
        
        # Verify network types
        network_names = [ntw.name for ntw in rf_circuit.networks_list]
        assert all(name in network_names for name in ['att1', 'iso1', 'spl1', 'cpl1'])
        
        # Verify connections
        assert len(rf_circuit.connections) == 2

    def test_frequency_validation(self, base_params):
        """Test frequency point compatibility validation"""
        # Create networks with incompatible frequencies
        incompatible_params = base_params.copy()
        incompatible_params['frequency'] = [2e9, 2.1e9, 2.2e9]
        
        with pytest.raises(ValueError, match="incompatible frequency points"):
            Circuit(
                networks={
                    'r1': R(r=50, **base_params),
                    'l1': L(l=1e-9, **incompatible_params)
                },
                connections=[[('r1', 0), ('l1', 0)]]
            )

    def test_connection_validation(self, base_params):
        """Test connection validation"""
        # Create circuit with invalid connection
        with pytest.raises(ValueError, match="Network 'invalid_network' not found in networks"):
            Circuit(
                networks={
                    'r1': R(r=50, **base_params)
                },
                connections=[[('r1', 0), ('invalid_network', 0)]]
            )

    def test_sim_circuit(self, base_params):
        """Test circuit with simulation components (Port, Ground, Open)"""
        # Create circuit with simulation components
        sim_circuit = Circuit(
            networks={
                'port1': Port(name="port1", **base_params),
                'ground1': Ground(name="ground1", **base_params),
                'open1': Open(name="open1", **base_params)
            },
            connections=[[('port1', 0), ('ground1', 0)],
                        [('open1', 0)]]
        )

        # Convert to scikit-rf circuit
        rf_circuit = sim_circuit.to_circuit()
        
        # Verify network count
        assert len(rf_circuit.networks_list) == 3
        
        # Verify network types and attributes
        for net in rf_circuit.networks_list:
            if net.name == 'port1':
                assert getattr(net, '_ext_attrs', {}).get('_is_circuit_port') is True
                assert net.s.shape == (3, 1, 1)  # 3 frequency points, 1-port
            elif net.name == 'ground1':
                assert getattr(net, '_ext_attrs', {}).get('_is_circuit_ground') is True
                assert net.s.shape == (3, 1, 1)
            elif net.name == 'open1':
                assert getattr(net, '_ext_attrs', {}).get('_is_circuit_open') is True
                assert net.s.shape == (3, 1, 1)

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
        assert len(rf_circuit.networks_list) == 4
        network_names = [ntw.name for ntw in rf_circuit.networks_list]
        assert all(name in network_names for name in ['r1', 'port1', 'ground1', 'att1'])
        
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
    test.test_sim_circuit(base_params())