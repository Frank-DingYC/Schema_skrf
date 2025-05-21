from pydantic.v1 import Field, validator
from tidy3d.components.base import Tidy3dBaseModel
from tidy3d.components.types import ArrayComplex1D, ArrayComplex2D, ArrayComplex3D, ArrayFloat1D, ComplexNumber
import skrf as rf
import numpy as np
from typing import List, Optional, Any, Union

class Network(Tidy3dBaseModel):
    """An n-port electrical network"""
    frequency: ArrayFloat1D = Field(
        ...,
        title="Frequency",
        description="Frequency points in Hz",
        example=[1e9, 2e9, 3e9]
    )
    s_parameters: ArrayComplex3D = Field(
        ...,
        title="S-Parameters",
        description="S-parameter matrix (n_freqs x n_ports x n_ports, complex)",
    )
    z0: Union[ArrayComplex2D, ArrayComplex1D] = Field(
        ...,
        title="Port Impedance",
        description="Impedance for each port at each frequency (n_freqs x n_ports, complex)",
    )
    name: Optional[str] = Field(
        None,
        title="Name",
        description="Network name",
        example="2-port_network"
    )
    nports: int = Field(
        ...,
        title="Number of Ports",
        description="Number of ports in the network",
        example=2
    )
    comments: Optional[List[str]] = Field(
        None,
        title="Comments",
        description="User comments about the network",
        example=["Measured 2023-05-01", "Calibrated with TRL"]
    )

    def __init__(self, **data: Any):
        super().__init__(**data)

    @validator('nports')
    def validate_nports(cls, v):
        """Validate number of ports"""
        if v <= 0:
            raise ValueError("Number of ports must be positive")
        return v

    @validator('frequency')
    def validate_frequency(cls, v):
        if not isinstance(v, np.ndarray):
            v = np.array(v)
        if v.size == 0:
            raise ValueError("Frequency array cannot be empty")
        if np.any(v < 0):
            raise ValueError("Frequencies must be strictly positive")
        return v

    @validator('z0')
    def validate_z0(cls, v, values):
        if 'nports' not in values or 'frequency' not in values:
            return v
        if not isinstance(v, np.ndarray):
            v = np.array(v)
        nports = values['nports']
        n_freqs = len(values['frequency'])
        if v.shape[0] != n_freqs:
            raise ValueError(f"z0 must have {n_freqs} frequency points")
        if v.shape[1] != nports:
            raise ValueError(f"Each z0 entry must have {nports} ports")
        return v

    @validator('s_parameters')
    def validate_s_parameters(cls, v, values):
        if 'nports' not in values or 'frequency' not in values:
            return v
        if not isinstance(v, np.ndarray):
            v = np.array(v)
        nports = values['nports']
        n_freqs = len(values['frequency'])
        if v.ndim != 3:
            raise ValueError("S-parameters must be a 3D array (n_freqs x n_ports x n_ports)")
        if v.shape[0] != n_freqs:
            raise ValueError(f"S-parameters must have {n_freqs} frequency points")
        if v.shape[1] != nports or v.shape[2] != nports:
            raise ValueError(f"Each S-parameter matrix must be {nports}x{nports}")
        return v

    @classmethod
    def from_network(cls, network: rf.Network) -> 'Network':
        return cls(
            frequency=list(network.f),
            s_parameters=network.s,
            z0=network.z0,
            name=network.name,
            nports=network.nports,
            comments=list(network.comments) if network.comments is not None else None
        )

    @classmethod
    def from_touchstone(cls, file_path: str) -> 'Network':
        network = rf.Network(file_path)
        return cls.from_network(network)

    def to_network(self) -> rf.Network:
        # Create frequency object
        freq = rf.Frequency.from_f(self.frequency, unit='Hz')
        
        # Create network object with frequency points
        network = rf.Network(frequency=freq, s=self.s_parameters, z0=self.z0, name=self.name)
        
        # Set metadata
        if self.comments:
            network.comments = self.comments
        
        return network

def interpolate_z0(z0: np.ndarray, source_freq: rf.Frequency, target_freq: rf.Frequency) -> np.ndarray:
    z0_interp = np.zeros((len(target_freq.f), z0.shape[1]), dtype=complex)
    for port in range(z0.shape[1]):
        z0_interp[:, port] = np.interp(target_freq.f, source_freq.f, z0[:, port])
    return z0_interp

def interpolate_s(snp: rf.Network, frequency_range: rf.Frequency, **kwargs) -> np.ndarray:
    vf = rf.VectorFitting(snp)
    vf_params = {'n_poles_real': 2, 'n_poles_cmplx': 4}
    vf_params.update(kwargs)
    vf.vector_fit(**vf_params)
    s_interpolated = np.zeros((len(frequency_range.f), snp.nports, snp.nports), dtype=complex)
    for i in range(snp.nports):
        for j in range(snp.nports):
            s_interpolated[:, i, j] = vf.get_model_response(i, j, frequency_range.f)
    return s_interpolated

def fit_frequency(snp: rf.Network, frequency_range: rf.Frequency, **kwargs) -> rf.Network:
    snp_range = snp.frequency
    if np.array_equal(snp_range.f, frequency_range.f):
        return snp
    s_interpolated = interpolate_s(snp, frequency_range, **kwargs)
    z0_interpolated = interpolate_z0(snp.z0, snp_range, frequency_range)
    return rf.Network(frequency=frequency_range, s=s_interpolated, z0=z0_interpolated, name=snp.name)

if __name__ == "__main__":
    import json
    with open('network.json','w') as f:
        network_schema = Network.schema()
        json.dump(network_schema, f, indent=4)