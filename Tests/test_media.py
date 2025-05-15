import pytest
import numpy as np
from Src.Models.Media import (
    RWG, CoaxialLine, CWG, CPWLine, MicrostripLine, DistributedRLGC
)

class BaseMediaTest:
    """Base class for media tests with common test logic""" 
    @pytest.fixture
    def frequency(self):
        """Common frequency range for testing"""
        return np.array([1e9, 5e9, 10e9])  # 1-10 GHz range

    def verify_media_object(self, media, expected_freq_len):
        """Verify basic properties of media object"""
        assert hasattr(media, 'frequency')
        assert len(media.frequency.f) == expected_freq_len

class TestCoaxialLine(BaseMediaTest):
    """Test suite for CoaxialLine class"""
    @pytest.fixture
    def basic_media(self, frequency):
        """Basic coaxial line configuration for testing"""
        return CoaxialLine(
            frequency=frequency,
            dinner=1e-3,  # 1mm inner diameter
            douter=3.5e-3,  # 3.5mm outer diameter
            z0=50
        )

    @pytest.fixture
    def default_params(self):
        """Default parameters for coaxial line"""
        return {
            'dinner': 1e-3,
            'douter': 3.5e-3,
            'epsilon_r': 1.0,
            'tan_delta': 0.0,
            'sigma': float('inf')
        }

    def test_default_initialization(self, basic_media, default_params):
        """Test initialization with default parameters"""
        for param, expected in default_params.items():
            assert getattr(basic_media, param) == expected

    @pytest.mark.parametrize('params', [
        {'dinner': 1e-3, 'douter': 3.5e-3},  # Minimum required
        {'dinner': 2e-3, 'douter': 7e-3, 'epsilon_r': 2.1,  # Full parameters
         'tan_delta': 0.001, 'sigma': 5.8e7}
    ])
    def test_initialization_with_parameters(self, frequency, params):
        """Test initialization with various parameter combinations"""
        media = CoaxialLine(frequency=frequency, z0=50, **params)
        for param, value in params.items():
            assert getattr(media, param) == value

    def test_media_creation(self, basic_media):
        """Test creation of scikit-rf media object"""
        media = basic_media.to_rf_media()
        self.verify_media_object(media, len(basic_media.frequency))
        
        # Verify specific coaxial parameters
        assert media.Dint == basic_media.dinner
        assert media.Dout == basic_media.douter

    @pytest.mark.parametrize('invalid_params,error_msg', [
        ({'dinner': -1e-3}, "Inner diameter must be positive"),
        ({'douter': -3.5e-3}, "Outer diameter must be positive"),
        ({'dinner': 3.5e-3, 'douter': 1e-3}, "Outer diameter must be greater than inner diameter"),
        ({'epsilon_r': -2.1}, "Relative permittivity must be positive"),
        ({'tan_delta': -0.001}, "Loss tangent must be non-negative"),
        ({'sigma': -5.8e7}, "Conductivity must be positive or infinity")
    ])
    def test_invalid_parameters(self, basic_media, invalid_params, error_msg):
        """Test validation of invalid parameters"""
        with pytest.raises(ValueError, match=error_msg):
            params = basic_media.dict()
            params.update(invalid_params)
            CoaxialLine(**params)

class TestRWG(BaseMediaTest):
    """Test suite for RWG (Rectangular Waveguide) class"""
    @pytest.fixture
    def basic_media(self, frequency):
        """Basic rectangular waveguide configuration for testing"""
        return RWG(
            frequency=frequency,
            a=22.86e-3,  # WR-90 width
            z0=50
        )

    @pytest.fixture
    def default_params(self):
        """Default parameters for rectangular waveguide"""
        return {
            'a': 22.86e-3,
            'b': None,
            'ep_r': 1.0,
            'mu_r': 1.0,
            'mode_type': 'TE',
            'm': 1,
            'n': 0,
            'rho': None,
            'roughness': None
        }

    def test_default_initialization(self, basic_media, default_params):
        """Test initialization with default parameters"""
        for param, expected in default_params.items():
            assert getattr(basic_media, param) == expected

    @pytest.mark.parametrize('params', [
        {'a': 22.86e-3},  # Minimum required (WR-90 width)
        {'a': 22.86e-3, 'b': 10.16e-3},  # With height (WR-90)
        {'a': 22.86e-3, 'b': 10.16e-3, 'ep_r': 2.1,  # Full parameters
         'mu_r': 1.5, 'mode_type': 'TM', 'm': 2, 'n': 1},
        {'a': 22.86e-3, 'rho': 1.68e-8},  # With conductor resistivity
        {'a': 22.86e-3, 'roughness': 0.5e-6}  # With surface roughness
    ])
    def test_initialization_with_parameters(self, frequency, params):
        """Test initialization with various parameter combinations"""
        media = RWG(frequency=frequency, z0=50, **params)
        for param, value in params.items():
            assert getattr(media, param) == value

    def test_media_creation(self, basic_media):
        """Test creation of scikit-rf media object"""
        media = basic_media.to_rf_media()
        self.verify_media_object(media, len(basic_media.frequency))
        
        # Verify specific RWG parameters
        assert media.a == basic_media.a
        if basic_media.b is not None:
            assert media.b == basic_media.b

    @pytest.mark.parametrize('invalid_params,error_type,error_msg', [
        ({'a': -1e-3}, ValueError, "Width must be positive"),
        ({'b': -10.16e-3}, ValueError, "Height must be positive"),
        ({'mode_type': 'Invalid'}, ValueError, "unexpected value; permitted: 'TE', 'TM'"),
        ({'m': -1}, ValueError, "Mode index m must be non-negative"),
        ({'n': -1}, ValueError, "Mode index n must be non-negative"),
        ({'rho': -1.68e-8}, ValueError, "Resistivity must be positive"),
        ({'roughness': -0.5e-6}, ValueError, "Roughness must be positive")
    ])
    def test_invalid_parameters(self, basic_media, invalid_params, error_type, error_msg):
        """Test validation of invalid parameters"""
        with pytest.raises((ValueError, Exception), match=error_msg):
            params = basic_media.dict()
            params.update(invalid_params)
            RWG(**params)   

class TestCWG(BaseMediaTest):
    """Test suite for CWG (Circular Waveguide) class"""
    @pytest.fixture
    def basic_media(self, frequency):
        """Basic circular waveguide configuration for testing"""
        return CWG(
            frequency=frequency,
            r=5e-3,  # 10mm diameter waveguide
            z0=50
        )

    @pytest.fixture
    def default_params(self):
        """Default parameters for circular waveguide"""
        return {
            'r': 5e-3,
            'ep_r': 1.0,
            'mu_r': 1.0,
            'mode_type': 'te',
            'm': 1,
            'n': 1,
            'rho': None
        }

    def test_default_initialization(self, basic_media, default_params):
        """Test initialization with default parameters"""
        for param, expected in default_params.items():
            assert getattr(basic_media, param) == expected

    @pytest.mark.parametrize('params', [
        {'r': 5e-3},  # Minimum required
        {'r': 5e-3, 'ep_r': 2.1, 'mu_r': 1.5},  # With material properties
        {'r': 5e-3, 'mode_type': 'tm', 'm': 2, 'n': 1}  # Different mode
    ])
    def test_initialization_with_parameters(self, frequency, params):
        """Test initialization with various parameter combinations"""
        media = CWG(frequency=frequency, z0=50, **params)
        for param, value in params.items():
            assert getattr(media, param) == value

    def test_media_creation(self, basic_media):
        """Test creation of scikit-rf media object"""
        media = basic_media.to_rf_media()
        self.verify_media_object(media, len(basic_media.frequency))
        
        # Verify specific CWG parameters
        assert media.r == basic_media.r  # both use radius
        assert media.ep_r == basic_media.ep_r
        assert media.mu_r == basic_media.mu_r

    @pytest.mark.parametrize('invalid_params,error_msg', [
        ({'r': -5e-3}, "Radius must be positive"),
        ({'ep_r': 0.5}, "Relative permittivity must be greater than 1"),
        ({'mu_r': 0.5}, "Relative permeability must be greater than 1"),
        ({'mode_type': 'invalid'}, "unexpected value; permitted: 'te', 'tm'"),
        ({'m': -1}, "Mode index m must be non-negative"),
        ({'n': -1}, "Mode index n must be positive")
    ])
    def test_invalid_parameters(self, basic_media, invalid_params, error_msg):
        """Test validation of invalid parameters"""
        with pytest.raises(ValueError, match=error_msg):
            params = basic_media.dict()
            params.update(invalid_params)
            CWG(**params)

class TestCPWLine(BaseMediaTest):
    """Test suite for CPWLine (Coplanar Waveguide) class"""
    @pytest.fixture
    def basic_media(self, frequency):
        """Basic CPWLine configuration for testing"""
        return CPWLine(
            frequency=frequency,
            w=0.5e-3,  # 500 µm center conductor
            s=0.2e-3,  # 200 µm gap
            z0=50
        )

    @pytest.fixture
    def default_params(self):
        """Default parameters for CPWLine"""
        return {
            'w': 0.5e-3,
            's': 0.2e-3,
            'h': 1.55,
            'ep_r': 4.5,
            't': None,
            'tand': 0.0,
            'rho': 1.68e-8,
            'has_metal_backside': False,
            'diel': 'djordjevicsvensson',
            'f_low': 1e3,
            'f_high': 1e12,
            'f_epr_tand': 1e9,
            'compatibility_mode': None
        }

    def test_default_initialization(self, basic_media, default_params):
        """Test initialization with default parameters"""
        for param, expected in default_params.items():
            assert getattr(basic_media, param) == expected

    @pytest.mark.parametrize('params', [
        {'w': 0.5e-3, 's': 0.2e-3},  # Minimum required
        {'w': 0.5e-3, 's': 0.2e-3, 'h': 0.5, 'ep_r': 3.2},  # Different substrate
        {'w': 0.5e-3, 's': 0.2e-3, 't': 35e-6, 'tand': 0.02},  # With metal thickness and losses
        {'w': 0.5e-3, 's': 0.2e-3, 'diel': 'frequencyinvariant'},  # Different dielectric model
        {'w': 0.5e-3, 's': 0.2e-3, 'compatibility_mode': 'qucs'},  # With compatibility mode
        {'w': 0.5e-3, 's': 0.2e-3, 'f_low': 1e2, 'f_high': 1e11, 'f_epr_tand': 2e9}  # Different frequency ranges
    ])
    def test_initialization_with_parameters(self, frequency, params):
        """Test initialization with various parameter combinations"""
        media = CPWLine(frequency=frequency, z0=50, **params)
        for param, value in params.items():
            assert getattr(media, param) == value

    def test_media_creation(self, basic_media):
        """Test creation of scikit-rf media object"""
        media = basic_media.to_rf_media()
        self.verify_media_object(media, len(basic_media.frequency))
        
        # Verify specific CPW parameters
        assert media.w == basic_media.w
        assert media.s == basic_media.s
        assert media.h == basic_media.h
        assert media.ep_r == basic_media.ep_r
        assert media.t == basic_media.t
        assert media.tand == basic_media.tand
        assert media.rho == basic_media.rho
        assert media.has_metal_backside == basic_media.has_metal_backside
        assert media.diel == basic_media.diel
        assert media.f_low == basic_media.f_low
        assert media.f_high == basic_media.f_high
        assert media.f_epr_tand == basic_media.f_epr_tand
        assert media.compatibility_mode == basic_media.compatibility_mode

    @pytest.mark.parametrize('invalid_params,error_msg', [
        ({'w': -0.5e-3}, "Width must be positive"),
        ({'s': -0.2e-3}, "Gap must be positive"),
        ({'h': -1.55}, "Height must be positive"),
        ({'ep_r': 0.5}, "Relative permittivity must be greater than 1"),
        ({'tand': -0.02}, "Loss tangent must be non-negative"),
        ({'diel': 'invalid'}, "unexpected value; permitted: 'djordjevicsvensson', 'frequencyinvariant'"),
        ({'f_low': -1e3}, "Low frequency must be positive"),
        ({'f_high': -1e12}, "High frequency must be positive"),
        ({'f_epr_tand': -1e9}, "Measurement frequency must be positive"),
        ({'f_low': 1e12, 'f_high': 1e3}, "High frequency must be greater than low frequency")
    ])
    def test_invalid_parameters(self, basic_media, invalid_params, error_msg):
        """Test validation of invalid parameters"""
        with pytest.raises(ValueError, match=error_msg):
            params = basic_media.dict()
            params.update(invalid_params)
            CPWLine(**params)


class TestMicrostripLine(BaseMediaTest):
    """Test suite for MicrostripLine class"""
    @pytest.fixture
    def basic_media(self, frequency):
        """Basic microstrip line configuration for testing"""
        return MicrostripLine(
            frequency=frequency,
            w=3e-3,  # 3mm width
            h=1.55e-3,  # 1.55mm height
            z0=50
        )

    @pytest.fixture
    def default_params(self):
        """Default parameters for microstrip line"""
        return {
            'w': 3e-3,
            'h': 1.55e-3,
            't': None,
            'ep_r': 4.5,
            'mu_r': 1.0,
            'model': 'hammerstadjensen',
            'disp': 'kirschningjansen',
            'tand': 0.0,
            'rho': 1.68e-8,
            'rough': None,
            'diel': 'djordjevicsvensson',
            'f_low': 1e3,
            'f_high': 1e12,
            'f_epr_tand': 1e9,
            'compatibility_mode': None
        }

    def test_default_initialization(self, basic_media, default_params):
        """Test initialization with default parameters"""
        for param, expected in default_params.items():
            assert getattr(basic_media, param) == expected

    @pytest.mark.parametrize('params', [
        {'w': 3e-3, 'h': 1.55e-3},  # Minimum required
        {'w': 3e-3, 'h': 1.55e-3, 't': 35e-6},  # With thickness
        {'w': 3e-3, 'h': 1.55e-3, 'ep_r': 2.1, 'mu_r': 1.5, 'tand': 0.001},  # With material properties
        {'w': 3e-3, 'h': 1.55e-3, 'rho': 2.65e-8, 'rough': 0.5e-6},  # With conductor properties
        {'w': 3e-3, 'h': 1.55e-3, 'model': 'wheeler', 'disp': 'kobayashi'},  # Different models
        {'w': 3e-3, 'h': 1.55e-3, 'diel': 'frequencyinvariant'},  # Different dielectric model
        {'w': 3e-3, 'h': 1.55e-3, 'compatibility_mode': 'qucs'}  # With compatibility mode
    ])
    def test_initialization_with_parameters(self, frequency, params):
        """Test initialization with various parameter combinations"""
        media = MicrostripLine(frequency=frequency, z0=50, **params)
        for param, value in params.items():
            assert getattr(media, param) == value

    def test_media_creation(self, basic_media):
        """Test creation of scikit-rf media object"""
        media = basic_media.to_rf_media()
        self.verify_media_object(media, len(basic_media.frequency))
        
        # Verify specific microstrip parameters
        assert media.w == basic_media.w
        assert media.h == basic_media.h
        assert media.t == basic_media.t
        assert media.ep_r == basic_media.ep_r
        assert media.mu_r == basic_media.mu_r
        assert media.model == basic_media.model
        assert media.disp == basic_media.disp
        assert media.tand == basic_media.tand
        assert media.rho == basic_media.rho
        assert media.rough == basic_media.rough
        assert media.diel == basic_media.diel
        assert media.f_low == basic_media.f_low
        assert media.f_high == basic_media.f_high
        assert media.f_epr_tand == basic_media.f_epr_tand
        assert media.compatibility_mode == basic_media.compatibility_mode

    @pytest.mark.parametrize('invalid_params,error_msg', [
        ({'w': -3e-3}, "Width must be positive"),
        ({'h': -1.55e-3}, "Height must be positive"),
        ({'t': -35e-6}, "Thickness must be positive"),
        ({'ep_r': 0.9}, "Relative permittivity must be greater than 1"),
        ({'mu_r': 0.9}, "Relative permeability must be greater than or equal to 1"),
        ({'tand': -0.001}, "Loss tangent must be non-negative"),
        ({'rho': -1.68e-8}, "Resistivity must be positive"),
        ({'rough': -0.5e-6}, "Surface roughness must be positive"),
        ({'model': 'invalid'}, "unexpected value; permitted: 'hammerstadjensen', 'schneider', 'wheeler'"),
        ({'disp': 'invalid'}, "unexpected value; permitted: 'hammerstadjensen', 'kirschningjansen', 'kobayashi', 'schneider', 'yamashita', 'none'"),
        ({'diel': 'invalid'}, "unexpected value; permitted: 'djordjevicsvensson', 'frequencyinvariant'"),
        ({'f_low': -1e3}, "f_low must be positive"),
        ({'f_high': -1e12}, "f_high must be positive"),
        ({'f_epr_tand': -1e9}, "f_epr_tand must be positive"),
        ({'f_low': 1e12, 'f_high': 1e3}, "f_high must be greater than f_low"),
        ({'compatibility_mode': 'invalid'}, "unexpected value; permitted: 'qucs', None")
    ])
    def test_invalid_parameters(self, basic_media, invalid_params, error_msg):
        """Test validation of invalid parameters"""
        with pytest.raises(ValueError, match=error_msg):
            params = basic_media.dict()
            params.update(invalid_params)
            MicrostripLine(**params)


class TestDistributedRLGC(BaseMediaTest):
    """Test suite for DistributedRLGC class"""
    @pytest.fixture
    def basic_media(self, frequency):
        """Basic distributed RLGC configuration for testing"""
        return DistributedRLGC(
            frequency=frequency,
            R=1.0,
            L=2e-9,
            G=0.1,
            C=2e-12
        )

    @pytest.fixture
    def default_params(self):
        """Default parameters for distributed RLGC"""
        return {
            'R': 0.0,
            'L': 1e-9,
            'G': 0.0,
            'C': 1e-12,
        }

    def test_default_initialization(self, basic_media, default_params):
        """Test initialization with default parameters"""
        media = DistributedRLGC(frequency=basic_media.frequency)
        for param, value in default_params.items():
            assert getattr(media, param) == value
        assert media.type == 'DistributedRLGC'

    @pytest.mark.parametrize('params', [
        {'R': 2.0, 'L': 3e-9},
        {'G': 0.2, 'C': 3e-12},
        {'R': 1.5, 'L': 2.5e-9, 'G': 0.15, 'C': 2.5e-12}
    ])
    def test_initialization_with_parameters(self, frequency, params):
        """Test initialization with various parameter combinations"""
        media = DistributedRLGC(frequency=frequency, **params)
        for param, value in params.items():
            assert getattr(media, param) == value

    def test_array_parameters(self, frequency):
        """Test initialization with array parameters"""
        R_array = np.array([1.0, 1.5, 2.0])
        L_array = np.array([1e-9, 1.5e-9, 2e-9])
        G_array = np.array([0.1, 0.15, 0.2])
        C_array = np.array([1e-12, 1.5e-12, 2e-12])
        
        media = DistributedRLGC(
            frequency=frequency,
            R=R_array,
            L=L_array,
            G=G_array,
            C=C_array,
        )
        
        assert np.array_equal(media.R, R_array)
        assert np.array_equal(media.L, L_array)
        assert np.array_equal(media.G, G_array)
        assert np.array_equal(media.C, C_array)

    def test_media_creation(self, basic_media):
        """Test creation of scikit-rf media object"""
        rf_media = basic_media.to_rf_media()
        assert np.array_equal(rf_media.frequency.f, basic_media.frequency)
        assert rf_media.R == basic_media.R
        assert rf_media.L == basic_media.L
        assert rf_media.G == basic_media.G
        assert rf_media.C == basic_media.C

    @pytest.mark.parametrize('invalid_params,error_msg', [
        ({'R': -1.0}, "Resistance must be non-negative"),
        ({'L': 0.0}, "Inductance must be positive"),
        ({'G': -0.1}, "Conductance must be non-negative"),
        ({'C': -1e-12}, "Capacitance must be positive")
    ])
    def test_invalid_parameters(self, basic_media, invalid_params, error_msg):
        """Test validation of invalid parameters"""
        with pytest.raises(ValueError, match=error_msg):
            params = basic_media.dict()
            params.update(invalid_params)
            DistributedRLGC(**params)