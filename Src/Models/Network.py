from pydantic.v1 import BaseModel, Field, validator
import skrf as rf
import numpy as np
from typing import List, Optional, Dict, Any, Union

class Network(BaseModel):
    frequency: List[float] = Field(
        ...,
        description="Frequency points in Hz",
        example=[1e9, 2e9, 3e9]
    )
    s_parameters: List[List[List[List[float]]]] = Field(
        ...,
        description="S-parameter matrix (n_freqs x n_ports x n_ports, [real, imag])",
        example=[[[[1.0, 0.0], [0.0, 1.0]], [[0.0, 1.0], [1.0, 0.0]]]]
    )
    z0: List[List[List[float]]] = Field(
        ...,
        description="Impedance for each port at each frequency (n_freqs x n_ports, [real, imag])",
        example=[[[50.0, 0.0], [50.0, 0.0]], [[50.0, 0.0], [50.0, 0.0]], [[50.0, 0.0], [50.0, 0.0]]]
    )
    name: Optional[str] = Field(
        None,
        description="Network name",
        example="2-port_network"
    )
    nports: int = Field(
        ...,
        description="Number of ports in the network",
        example=2
    )
    comments: Optional[List[str]] = Field(
        None,
        description="User comments about the network",
        example=["Measured 2023-05-01", "Calibrated with TRL"]
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            np.ndarray: lambda v: v.tolist(),
            complex: lambda v: [v.real, v.imag]
        }

    def __init__(self, **data: Any):
        super().__init__(**data)  # Call Pydantic's __init__ for validation

    @validator('nports')
    def validate_nports(cls, v, values):
        if v <= 0:
            raise ValueError("Number of ports must be positive")
        if 's_parameters' in values and values['s_parameters']:
            if any(len(matrix) != v or any(len(row) != v for row in matrix) for matrix in values['s_parameters']):
                raise ValueError(f"S-parameters must be {v}x{v} matrices")
        if 'z0' in values and values['z0']:
            if any(len(inner) != v for inner in values['z0']):
                raise ValueError(f"z0 must have {v} ports")
        return v

    @validator('frequency')
    def validate_frequency(cls, v):
        if not v:
            raise ValueError("Frequency list cannot be empty")
        if any(f < 0 for f in v):
            raise ValueError("Frequencies must be strictly positive")
        return v

    @validator('z0')
    def validate_z0(cls, v, values):
        if 'nports' not in values or 'frequency' not in values:
            return v
        nports = values['nports']
        n_freqs = len(values['frequency'])
        if len(v) != n_freqs:
            raise ValueError(f"z0 must have {n_freqs} frequency points")
        if any(len(inner) != nports for inner in v):
            raise ValueError(f"Each z0 entry must have {nports} ports")
        return [[(complex(real, imag).real, complex(real, imag).imag) for real, imag in inner] for inner in v]

    @validator('s_parameters')
    def validate_s_parameters(cls, v, values):
        if 'nports' not in values or 'frequency' not in values:
            return v
        nports = values['nports']
        n_freqs = len(values['frequency'])
        if len(v) != n_freqs:
            raise ValueError(f"S-parameters must have {n_freqs} frequency points")
        for matrix in v:
            if len(matrix) != nports or any(len(row) != nports for row in matrix):
                raise ValueError(f"S-parameters must be {nports}x{nports} matrices")
        return [
            [[(complex(real, imag).real, complex(real, imag).imag) for real, imag in row] for row in matrix]
            for matrix in v
        ]

    @classmethod
    def from_network(cls, network: rf.Network) -> 'Network':
        s_parameters = [
            [[(sp.real, sp.imag) for sp in row] for row in matrix]
            for matrix in network.s
        ]
        z0 = [[(z.real, z.imag) for z in inner] for inner in network.z0]
        return cls(
            frequency=list(network.f),
            s_parameters=s_parameters,
            z0=z0,
            name=network.name,
            nports=network.nports,
            comments=list(network.comments) if network.comments is not None else None
        )

    @classmethod
    def from_touchstone(cls, file_path: str) -> 'Network':
        network = rf.Network(file_path)
        return cls.from_network(network)

    def to_network(self) -> rf.Network:
        freq = rf.Frequency.from_f(self.frequency, unit='Hz')
        s = np.array([
            [[complex(real, imag) for real, imag in row] for row in matrix]
            for matrix in self.s_parameters
        ])
        z0 = np.array([[complex(real, imag) for real, imag in inner] for inner in self.z0])
        network = rf.Network(frequency=freq, s=s, z0=z0, name=self.name)
        network.comments = self.comments
        return network

    @classmethod
    def from_json(cls, json_data: Dict) -> 'Network':
        return cls(**json_data)

    @classmethod
    def cascade(cls, network1: 'Network', network2: 'Network') -> 'Network':
        skrf_network1 = network1.to_network()
        skrf_network2 = network2.to_network()
        if not np.array_equal(skrf_network1.f, skrf_network2.f):
            freq = rf.Frequency.from_f(np.union1d(skrf_network1.f, skrf_network2.f), unit='Hz')
            skrf_network1 = fit_frequency(skrf_network1, freq)
            skrf_network2 = fit_frequency(skrf_network2, freq)
        cascaded_skrf = rf.cascade(skrf_network1, skrf_network2)
        return cls.from_network(cascaded_skrf)

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
    pass
    # import json
    # with open('network.json','w') as f:
    #     network_schema = Network.schema()
    #     json.dump(network_schema, f)