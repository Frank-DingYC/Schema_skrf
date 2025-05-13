import os
import skrf as rf
from Src.Models.Network import Network
import pytest
import numpy as np
from pydantic.v1.error_wrappers import ValidationError
from typing import List
import re

def get_touchstone_files(directory: str) -> List[str]:
    """Helper function to get all Touchstone files in the directory with pattern s*p, where * can be any digit."""
    touchstone_pattern = re.compile(r'\.s\d+p$')
    return [os.path.join(directory, f) for f in os.listdir(directory) if touchstone_pattern.search(f)]

def test_all_touchstone_files():
    # Test all Touchstone files in the directory
    directory = './data/Touchstone'
    files = get_touchstone_files(directory)

    for file_path in files:
        # Load network from Touchstone file
        network = Network.from_touchstone(file_path)
        assert isinstance(network, Network)
        assert len(network.z0) == len(network.frequency)
        assert len(network.z0[0]) == network.nports

        # Compare with skrf network
        skrf_network = rf.Network(file_path)
        network_schema = Network.from_network(skrf_network)
        new_skrf_network = network_schema.to_network()
        assert np.allclose(skrf_network.s, new_skrf_network.s)
        assert np.allclose(skrf_network.z0, new_skrf_network.z0)
        serialized = network_schema.json()
        assert isinstance(serialized, str)

def test_network_json_serialization():
    # Test JSON serialization of a network
    skrf_network = rf.Network('./data/Touchstone/cst_example_4ports.s4p')
    network_schema = Network.from_network(skrf_network)
    serialized = network_schema.json()
    assert isinstance(serialized, str)
    deserialized_network = Network.parse_raw(serialized)
    assert network_schema.name == deserialized_network.name
    assert np.allclose(network_schema.z0, deserialized_network.z0)
    assert np.allclose(network_schema.frequency, deserialized_network.frequency)

def test_z0_dimension_validation():
    # Test validation of z0 dimensions
    frequency = [1e9, 2e9]
    s_parameters = [
        [[[1.0, 0.0], [0.0, 1.0]], [[0.0, 1.0], [1.0, 0.0]]],
        [[[0.9, 0.1], [0.1, 0.9]], [[0.1, 0.9], [0.9, 0.1]]]
    ]
    nports = 2

    # Test case 1: z0 has fewer ports than nports (1 port instead of 2)
    invalid_z0_ports = [[[50.0, 0.0]], [[50.0, 0.0]]]
    with pytest.raises(ValidationError):
        Network(
            frequency=frequency,
            s_parameters=s_parameters,
            z0=invalid_z0_ports,
            nports=nports
        )

def test_s_parameters_validation():
    # Test validation of s-parameters
    invalid_s_parameters = [[[1.0, 0.0]], [[0.9, 0.1]]]
    with pytest.raises(ValidationError):
        Network(
            frequency=[1e9, 2e9],
            s_parameters=invalid_s_parameters,
            z0=[[[50.0, 0.0], [50.0, 0.0]], [[50.0, 0.0], [50.0, 0.0]]],
            nports=2
        )