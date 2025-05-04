import pytest
from Src.Models.RLGC import R, L, G, C, DistributedCircuit
import skrf as rf
import numpy as np

@pytest.fixture
def base_params():
    return {
        'frequency': list(np.linspace(1e9, 2e9, 100)),
        'z0': [[50.0, 0.0]]*100,
        'nports': 2
    }

class TestR:
    def test_r_creation(self, base_params):
        r_model = R(r=100.0, **base_params)
        assert isinstance(r_model.to_r(), rf.Network)


class TestL:

    @pytest.mark.parametrize('params', [
        {'l': 1e-9},
        {'l': 1e-9, 'f_0': 1e9, 'q_factor': 10},
        {'l': 1e-9, 'f_0': 1e9, 'q_factor': 10, 'r_dc': 0.1}
    ])
    def test_l_parameter_variants(self, base_params, params):
        l_model = L(**params, **base_params)
        network = l_model.to_l()
        assert isinstance(network, rf.Network)
    
    @pytest.mark.parametrize('params', [
        {'l': 1e-9, 'f_0': 1e9},
        {'l': 1e-9, 'q_factor': 10},
    ])
    def test_l_invalid_parameters(self, base_params, params):
        with pytest.raises(ValueError):
            l_model = L(**params, **base_params)
            l_model.to_l()

class TestG:
    def test_g_creation(self, base_params):
        g_model = G(g=1e-9, **base_params)
        network = g_model.to_g()
        assert isinstance(network, rf.Network)

class TestC:

    @pytest.mark.parametrize('params', [
        {'c': 1e-12},
        {'c': 1e-12, 'f_0': 1e9, 'q_factor': 10},
        {'c': 1e-12, 'f_0': 1e9, 'q_factor': 10, 'r_dc': 0.1}
    ])
    def test_c_parameter_variants(self, base_params, params):
        c_model = C(**params, **base_params)
        network = c_model.to_c()
        assert isinstance(network, rf.Network)
    
    @pytest.mark.parametrize('params', [
        {'c': 1e-12, 'q_factor': 10},
        {'c': 1e-12, 'f_0': 1e9},
    ])
    def test_c_invalid_parameters(self, base_params, params):
        with pytest.raises(ValueError):
            c_model = C(**params, **base_params)
            c_model.to_c()