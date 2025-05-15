import pytest
from Src.Models.Component import R, L, G, C, Attenuator, Isolator, Splitter, Coupler, Port, Ground, Open
from Src.Models.Media import CoaxialLine, MicrostripLine, DistributedRLGC, RWG, CWG, CPWLine
import skrf as rf
import numpy as np

@pytest.fixture
def base_params():
    """Basic parameters for component testing"""
    return {
        'frequency': list(np.linspace(1e9, 2e9, 100))
    }

@pytest.fixture
def test_media(base_params):
    """Fixture providing all available media types"""
    freq = base_params['frequency']
    
    media = [
        # Coaxial line
        CoaxialLine(
            frequency=freq,
            dinner=2e-3,  # Inner diameter
            douter=6e-3   # Outer diameter
        ),
        # Rectangular waveguide
        RWG(
            frequency=freq,
            a=1e-2,  # Width
            b=5e-3,  # Height
            mode_type='TE'
        ),
        # Circular waveguide
        CWG(
            frequency=freq,
            r=5e-3,  # Radius
            mode_type='te'
        ),
        # Coplanar waveguide
        CPWLine(
            frequency=freq,
            w=3e-3,  # Width
            s=0.3e-3,  # Gap
            h=1.55  # Height
        ),
        # Microstrip line
        MicrostripLine(
            frequency=freq,
            w=1e-3,  # Width
            h=0.5e-3  # Height
        ),
        # Distributed RLGC
        DistributedRLGC(
            frequency=freq,
            R=1.0,
            L=2e-9,
            G=0.1,
            C=2e-12
        )
    ]
    return media

class TestR:
    """Test Resistor component"""
    def test_r_creation(self, base_params):
        r_model = R(r=100.0, **base_params)
        assert isinstance(r_model.to_network(), rf.Network)

    def test_r_with_different_media(self):
        """Test resistor with different transmission line media"""
        freq = np.linspace(1e9, 2e9, 100)
        r_model = R(r=50, frequency=freq)

        # Test with coaxial line
        coax = CoaxialLine(
            frequency=freq,
            dinner=2e-3,  # Inner diameter
            douter=6e-3   # Outer diameter
        )
        network_coax = r_model.to_network(media=coax)
        assert isinstance(network_coax, rf.Network)
        assert network_coax.nports == 2

        # Test with microstrip line
        mline = MicrostripLine(
            frequency=freq,
            w=1e-3,  # Width
            h=0.5e-3  # Height
        )
        network_mline = r_model.to_network(media=mline)
        assert isinstance(network_mline, rf.Network)
        assert network_mline.nports == 2

        # Test with distributed RLGC
        rlgc = DistributedRLGC(
            frequency=freq,
            R=1.0,
            L=2e-9,
            G=0.1,
            C=2e-12
        )
        network_rlgc = r_model.to_network(media=rlgc)
        assert isinstance(network_rlgc, rf.Network)
        assert network_rlgc.nports == 2

    def test_r_impedance(self):
        # Test with default z0
        r_model = R(r=100.0, frequency=list(np.linspace(1e9, 2e9, 100)))
        assert r_model.z0 == 50
        assert r_model.z0_port == 50
        # Default z0 should be 50 ohms if not specified
        network = r_model.to_network()
        assert np.all(network.z0 == 50.0)

        # Test with custom z0
        z0_custom = 75+5j
        r_model = R(r=100.0, frequency=list(np.linspace(1e9, 2e9, 100)), z0=z0_custom)
        assert r_model.z0 == z0_custom
        assert r_model.z0_port == 50
        network = r_model.to_network()
        assert np.all(network.z0 == 50)

        # Test with both z0 and z0_port
        z0_port_custom = 25+0j
        r_model = R(r=100.0, frequency=list(np.linspace(1e9, 2e9, 100)),
                   z0=z0_custom, z0_port=z0_port_custom)
        assert r_model.z0 == z0_custom
        assert r_model.z0_port == z0_port_custom
        network = r_model.to_network()
        assert np.all(network.z0 == z0_port_custom)

        # Test with array-based z0 and z0_port
        freq = list(np.linspace(1e9, 2e9, 100))
        z0_array = 50 + 5j * np.linspace(0, 1, len(freq))
        z0_port_array = 75 + 2j * np.linspace(0, 1, len(freq))
        r_model = R(r=100.0, frequency=freq,
                   z0=z0_array, z0_port=z0_port_array)
        assert np.all(r_model.z0 == z0_array)
        network = r_model.to_network()
        assert np.all(network.z0[:, 0] == z0_port_array)
        assert np.all(network.z0[:, 1] == z0_port_array)

        
    def test_r_array_parameter(self):
        """Test resistor with array resistance"""
        freq = np.array(np.linspace(1e9, 2e9, 100), dtype=float)
        r_values = np.array(50 + 10 * np.sin(2 * np.pi * freq / 1e9), dtype=float)  # Frequency-dependent resistance
        r_model = R(r=r_values, frequency=freq)
        network = r_model.to_network()
        
        # Verify network properties
        assert network.nports == 2
        assert network.f.size == len(freq)
        assert network.s.shape == (len(freq), 2, 2)
        
    def test_r_frequency_mismatch(self):
        """Test validation error when resistance array length doesn't match frequency points"""
        freq = np.array(np.linspace(1e9, 2e9, 100), dtype=float)
        r_values = np.array(np.linspace(50, 100, 50), dtype=float)  # Only 50 points vs 100 frequency points
        
        with pytest.raises(ValueError, match="must match the number of frequency points"):
            R(r=r_values, frequency=freq)

class TestL:
    """Test Inductor component"""
    @pytest.mark.parametrize('params', [
        {'l': 1e-9},
        {'l': 1e-9, 'f_0': 1e9, 'q_factor': 10},
        {'l': 1e-9, 'f_0': 1e9, 'q_factor': 10, 'r_dc': 0.1}
    ])
    def test_l_parameter_variants(self, base_params, params):
        l_model = L(**params, **base_params)
        network = l_model.to_network()
        assert isinstance(network, rf.Network)
    
    @pytest.mark.parametrize('params', [
        {'l': 1e-9, 'f_0': 1e9},
        {'l': 1e-9, 'q_factor': 10},
    ])
    def test_l_invalid_parameters(self, base_params, params):
        with pytest.raises(ValueError):
            l_model = L(**params, **base_params)
            l_model.to_network()

    def test_l_array_parameter(self):
        """Test inductor with array inductance"""
        freq = np.linspace(1e9, 2e9, 100)
        l_values = 1e-9 + 0.5e-9 * np.sin(2 * np.pi * freq / 1e9)  # Frequency-dependent inductance
        l_model = L(l=l_values, frequency=freq)
        network = l_model.to_network()
        
        # Verify network properties
        assert network.nports == 2
        assert network.f.size == len(freq)
        assert network.s.shape == (len(freq), 2, 2)
        
    def test_l_frequency_mismatch(self):
        """Test validation error when inductance array length doesn't match frequency points"""
        freq = np.array(np.linspace(1e9, 2e9, 100), dtype=float)
        l_values = np.array(np.linspace(1e-9, 2e-9, 80), dtype=float)  # Only 80 points vs 100 frequency points
        
        with pytest.raises(ValueError, match="must match the number of frequency points"):
            L(l=l_values, frequency=freq)


class TestG:
    """Test Conductance component"""
    def test_g_creation(self, base_params):
        g_model = G(g=0.01, **base_params)
        assert isinstance(g_model.to_network(), rf.Network)

    def test_g_with_different_media(self):
        """Test conductance with different transmission line media"""
        freq = np.linspace(1e9, 2e9, 100)
        g_model = G(g=0.01, frequency=freq)

        # Test with coaxial line
        coax = CoaxialLine(
            frequency=freq,
            dinner=2e-3,  # Inner diameter
            douter=6e-3   # Outer diameter
        )
        network_coax = g_model.to_network(media=coax)
        assert isinstance(network_coax, rf.Network)
        assert network_coax.nports == 2

        # Test with microstrip line
        mline = MicrostripLine(
            frequency=freq,
            w=1e-3,  # Width
            h=0.5e-3  # Height
        )
        network_mline = g_model.to_network(media=mline)
        assert isinstance(network_mline, rf.Network)
        assert network_mline.nports == 2

        # Test with distributed RLGC
        rlgc = DistributedRLGC(
            frequency=freq,
            R=1.0,
            L=2e-9,
            G=0.1,
            C=2e-12
        )
        network_rlgc = g_model.to_network(media=rlgc)
        assert isinstance(network_rlgc, rf.Network)
        assert network_rlgc.nports == 2
        
    def test_g_array_parameter(self):
        """Test conductance with array conductance"""
        freq = np.linspace(1e9, 2e9, 100)
        g_values = 0.01 + 0.005 * np.sin(2 * np.pi * freq / 1e9)  # Frequency-dependent conductance
        g_model = G(g=g_values, frequency=freq)
        network = g_model.to_network()
        
        # Verify network properties
        assert network.nports == 2
        assert network.f.size == len(freq)
        assert network.s.shape == (len(freq), 2, 2)
        
    def test_g_frequency_mismatch(self):
        """Test validation error when conductance array length doesn't match frequency points"""
        freq = np.array(np.linspace(1e9, 2e9, 100), dtype=float)
        g_values = np.array(np.linspace(0.01, 0.02, 120), dtype=float)  # 120 points vs 100 frequency points
        
        with pytest.raises(ValueError, match="must match the number of frequency points"):
            G(g=g_values, frequency=freq)


class TestC:
    """Test Capacitor component"""
    @pytest.mark.parametrize('params', [
        {'c': 1e-12},
        {'c': 1e-12, 'f_0': 1e9, 'q_factor': 10},
        {'c': 1e-12, 'f_0': 1e9, 'q_factor': 10, 'r_dc': 0.1}
    ])
    def test_c_parameter_variants(self, base_params, params):
        c_model = C(**params, **base_params)
        network = c_model.to_network()
        assert isinstance(network, rf.Network)
    
    @pytest.mark.parametrize('params', [
        {'c': 1e-12, 'q_factor': 10},
        {'c': 1e-12, 'f_0': 1e9},
    ])
    def test_c_invalid_parameters(self, base_params, params):
        with pytest.raises(ValueError):
            c_model = C(**params, **base_params)
            c_model.to_network()

    def test_c_array_parameter(self):
        """Test capacitor with array capacitance"""
        freq = np.linspace(1e9, 2e9, 100)
        c_values = 1e-12 + 0.5e-12 * np.sin(2 * np.pi * freq / 1e9)  # Frequency-dependent capacitance
        c_model = C(c=c_values, frequency=freq)
        network = c_model.to_network()
        
        # Verify network properties
        assert network.nports == 2
        assert network.f.size == len(freq)
        assert network.s.shape == (len(freq), 2, 2)
        
    def test_c_frequency_mismatch(self):
        """Test validation error when capacitance array length doesn't match frequency points"""
        freq = np.array(np.linspace(1e9, 2e9, 100), dtype=float)
        c_values = np.array(np.linspace(1e-12, 2e-12, 90), dtype=float)  # Only 90 points vs 100 frequency points
        
        with pytest.raises(ValueError, match="must match the number of frequency points"):
            C(c=c_values, frequency=freq)


class TestAttenuator:
    """Test Attenuator component"""
    @pytest.mark.parametrize('params', [
        {'s21': -3},
        {'s21': 0.5, 'db': False},
        {'s21': -6, 'd': 5, 'unit': 'ns'}
    ])
    def test_attenuator_parameter_variants(self, base_params, params):
        atten = Attenuator(**params, **base_params)
        network = atten.to_network()
        assert isinstance(network, rf.Network)
        assert network.s.shape == (len(base_params['frequency']), 2, 2)

    def test_attenuator_array_parameter(self):
        """Test attenuator with array s21"""
        freq = np.linspace(1e9, 2e9, 100)
        # Frequency-dependent attenuation (in dB)
        s21_values = 3 + np.sin(2 * np.pi * freq / 1e9)
        
        # Test with dB values
        att_model = Attenuator(s21=s21_values, db=True, frequency=freq)
        network = att_model.to_network()
        assert network.nports == 2
        assert network.f.size == len(freq)
        assert network.s.shape == (len(freq), 2, 2)
        
        # Test with linear values
        s21_linear = 10**(-s21_values/20)  # Convert dB to linear scale
        att_model = Attenuator(s21=s21_linear, db=False, frequency=freq)
        network = att_model.to_network()
        assert network.nports == 2
        assert network.f.size == len(freq)
        assert network.s.shape == (len(freq), 2, 2)
        
    def test_attenuator_frequency_mismatch(self):
        """Test validation error when s21 array length doesn't match frequency points"""
        freq = np.array(np.linspace(1e9, 2e9, 100), dtype=float)
        # Only 75 points vs 100 frequency points
        s21_values = np.array(3 + np.sin(2 * np.pi * np.linspace(1e9, 2e9, 75) / 1e9), dtype=float)
        
        with pytest.raises(ValueError, match="must match the number of frequency points"):
            Attenuator(s21=s21_values, db=True, frequency=freq)
            
        # Test with linear values too
        s21_linear = 10**(-s21_values/20)
        with pytest.raises(ValueError, match="must match the number of frequency points"):
            Attenuator(s21=s21_linear, db=False, frequency=freq)


class TestIsolator:
    @pytest.mark.parametrize('source_port', [0, 1])
    def test_isolator_direction(self, base_params, source_port):
        iso = Isolator(source_port=source_port, **base_params)
        network = iso.to_network()
        assert isinstance(network, rf.Network)
        if source_port == 0:
            assert np.all(np.abs(network.s[:,0,1]) < 1e-6)
        else:
            assert np.all(np.abs(network.s[:,1,0]) < 1e-6)
    
    @pytest.mark.parametrize('params', [
        {'source_port': 2}
    ])
    def test_invalid_source_port(self, base_params, params):
        with pytest.raises(ValueError):
            iso = Isolator(**params, **base_params)
            iso.to_network()

class TestSplitter:
    """Test Splitter component"""
    @pytest.mark.parametrize('nports', [3, 4])
    def test_splitter_ports(self, base_params, nports):
        """Validate splitter S-parameters using theoretical formula:
        S_ij = 2*sqrt(Z0i*Z0j) / (Z0i*Σ(1/Z0k)) for i≠j
        S_ii = 1 - 2/Z0i * Σ(1/Z0k) for matched ports"""
        
        # Initialize splitter with specified port count
        splitter = Splitter(nports=nports, **base_params)
        network = splitter.to_network()
        
        # Basic network validation
        assert network.nports == nports, "Port count mismatch"
        assert network.s.shape == (len(base_params['frequency']), nports, nports)
        
        # Extract real part of Z0 (assuming lossless)
        z0 =[splitter.z0] * nports
        
        # Theoretical calculations
        s_matrix = network.s
        z0_sum = 1/z0[0] * nports
            
        # Verify off-diagonal elements (transmission)
        for i in range(nports):
            for j in range(nports):
                if i != j:
                    # Calculate theoretical S_ij
                    s_theory = 2 * np.sqrt(z0[i].real*z0[j].real) / (z0[i] * z0[j] * z0_sum)
                    assert np.allclose(abs(s_matrix[:,i,j]), abs(s_theory), atol=1e-3), \
                            f"S{i+1}{j+1} mismatch"
                    
            # Verify diagonal elements (reflection)
            s_reflection = 1 - 2/(z0[i] * z0_sum)
            assert np.allclose(abs(s_matrix[:,i,i]), abs(s_reflection), atol=1e-3), \
                f"S{i+1}{i+1} mismatch"

def test_components_with_all_media(base_params, test_media):
    """Test all components with all available media types"""
    freq = base_params['frequency']
    
    # List of component classes and their required parameters
    components = [
        (R, {'r': 50}),
        (L, {'l': 1e-9}),
        (G, {'g': 0.02}),
        (C, {'c': 1e-12}),
        (Attenuator, {'s21': 0.1, 'db': False}),  # 0.1 = -20dB attenuation
        (Isolator, {'source_port': 0}),
        (Splitter, {'nports': 3}),
        (Coupler, {'db': 3, 'deg': 0}),
        (Port, {'name': 'test_port'}),
        (Ground, {'name': 'test_ground'}),
        (Open, {'name': 'test_open'})
    ]
    
    # Test each component with each media type
    for component_class, params in components:
        # Create component instance
        component = component_class(
            frequency=freq,
            **params
        )
        
        # Test with each media type
        for media in test_media:
            # Convert component to network with the given media
            if isinstance(component, (Port, Ground, Open)):
                # These components don't accept media parameter
                network = component.to_network(z0_port=50)
            else:
                network = component.to_network(media=media)
                
            # Basic assertions
            assert isinstance(network, rf.Network)
            if not isinstance(component, (Port, Ground, Open)):
                # These components don't use the frequency parameter
                assert network.frequency.f.tolist() == freq
            
            # Check number of ports based on component type
            if isinstance(component, Splitter):
                assert network.nports == component.nports
            elif isinstance(component, Coupler):
                assert network.nports == 4  # Couplers always have 4 ports
            elif isinstance(component, (R, L, G, C, Attenuator, Isolator, Port, Ground, Open)):
                assert network.nports == 1 or network.nports == 2

class TestCoupler:
    """Test Coupler component"""
    @pytest.mark.parametrize('params', [
        {'db': -3, 'deg': -180},
        {'db': 5, 'deg': 900},
    ])
    def test_coupler_creation(self, base_params, params):
        # Test basic creation with valid parameters
        coupler = Coupler(**params, **base_params)
        network = coupler.to_network()
        assert isinstance(network, rf.Network)
        assert network.frequency.npoints == len(base_params['frequency'])

    @pytest.mark.parametrize('params', [
        {'db': '-3/2', 'deg': -180},
        {'db': 5, 'deg': '900*8'},
    ])
    def test_coupler_invalid_parameters(self, base_params, params):
        # Test parameter validation
        with pytest.raises(ValueError):
            coupler =Coupler(**params, **base_params)  # Wrong type
            coupler.to_network()

class TestPort:
    def test_port_creation(self, base_params):
        """Test creation of a Port component and verify network properties"""
        port_name = "test_port"
        port_model = Port(name=port_name, **base_params)
        network = port_model.to_network()
        
        # Verify network properties
        assert isinstance(network, rf.Network)
        assert network.name == port_name

    def test_port_impedance(self):
        """Test Port component with different impedance configurations"""
        port_name = "test_port"
        freq = list(np.linspace(1e9, 2e9, 100))

        # Test default impedance
        port = Port(name=port_name, frequency=freq)
        network = port.to_network()
        assert np.all(network.z0 == 50.0)

        # Test custom z0_port
        z0_custom = 75.0
        port = Port(name=port_name, frequency=freq)
        network = port.to_network(z0_port=z0_custom)
        assert np.all(network.z0 == z0_custom)
        assert network.s.shape == (len(freq), 1, 1)
        
        # Verify S-parameters (should be 0 for perfect match)
        assert np.allclose(abs(network.s), 0)
        
        # Verify the port attribute is set
        assert network._is_circuit_port is True

class TestGround:
    def test_ground_creation(self, base_params):
        """Test creation of a Ground component and verify network properties"""
        ground_name = "test_ground"
        ground_model = Ground(name=ground_name, **base_params)
        network = ground_model.to_network()
        
        # Verify network properties
        assert isinstance(network, rf.Network)
        assert network.name == ground_name
        assert network.s.shape == (len(base_params['frequency']), 2, 2)
        
        # Verify S-parameters (should be -1 for perfect short)
        assert np.allclose(network.s, [[-1, 0], [0, -1]])

class TestOpen:
    def test_open_creation(self, base_params):
        """Test creation of an Open component and verify network properties"""
        open_name = "test_open"
        open_model = Open(name=open_name, **base_params)
        network = open_model.to_network()
        
        # Verify network properties
        assert isinstance(network, rf.Network)
        assert network.name == open_name
        assert network.s.shape == (len(base_params['frequency']), 2, 2)
        
        # Verify S-parameters (should be 1 for perfect open)
        assert np.allclose(network.s, [[1, 0], [0, 1]])
if __name__ == '__main__':
    test = TestR()
    test.test_r_frequency_mismatch()