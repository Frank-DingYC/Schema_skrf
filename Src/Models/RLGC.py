from pydantic.v1 import BaseModel, Field, validator
from typing import List, Union, Optional, Any
import skrf as rf

class DistributedCircuit(BaseModel):
    frequency: List[float] = Field(
        ...,
        description="Frequency points in Hz",
        example=[1e9, 2e9, 3e9]
    )
    z0: List[List[float]] = Field(
        ...,
        description="Impedance for each port at each frequency (n_freqs x n_ports, [real, imag])",
        example=[[[50.0, 0.0], [50.0, 0.0]], [[50.0, 0.0], [50.0, 0.0]], [[50.0, 0.0], [50.0, 0.0]]]
    )
    nports: int = Field(
        2,
        description="Number of ports in the distributed circuit",
        example=2
    )

    def __init__(self, **data: Any):
        super().__init__(**data)

class R(DistributedCircuit):
    r: Union[float, List[float]] = Field(
        ...,
        description="Resistance"
    )

    def to_r(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        return line.resistor(self.r)

class L(DistributedCircuit):
    l: Union[float, List[float]] = Field(
        ...,
        description="Inductance"
    )
    f_0: Optional[float] = Field(
        None,
        description="Resonant frequency, in Hz"
    )
    q_factor: Optional[float] = Field(
        None,
        description="Quality factor"
    )
    r_dc: Optional[float] = Field(
        None,
        description="DC resistance"
    )

    def to_l(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        if self.f_0 is None and self.q_factor is None:
            return line.inductor(self.l)
        elif self.f_0 is not None and self.q_factor is not None:
            if self.r_dc is not None:
                return line.inductor_q(self.l, f_0=self.f_0, q_factor=self.q_factor, r_dc=self.r_dc)
            else:
                return line.inductor_q(self.l, f_0=self.f_0, q_factor=self.q_factor)
        else:
            raise ValueError("f_0 and q_factor must be both specified or both None")

class C(DistributedCircuit):
    c: Union[float, List[float]] = Field(
        ...,
        description="Capacitance"
    )
    f_0: Optional[float] = Field(
        None,
        description="Resonant frequency, in Hz"
    )
    q_factor: Optional[float] = Field(
        None,
        description="Quality factor"
    )
    r_dc: Optional[float] = Field(
        None,
        description="DC resistance"
    )

    def to_c(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        if self.f_0 is None and self.q_factor is None:
            return line.capacitor(self.c)
        elif self.f_0 is not None and self.q_factor is not None:
            if self.r_dc is not None:
                return line.capacitor_q(self.c, f_0=self.f_0, q_factor=self.q_factor, r_dc=self.r_dc)
            else:
                return line.capacitor_q(self.c, f_0=self.f_0, q_factor=self.q_factor)
        else:
            raise ValueError("f_0 and q_factor must be both specified or both None")

class G(DistributedCircuit):
    g: Union[float, List[float]] = Field(
        ...,
        description="Conductance"
    )

    def to_g(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        return line.shunt_resistor(self.g)
RLGC = Union[R, L, G, C]