from pydantic.v1 import BaseModel, Field, validator
from typing import List, Literal, Union, Optional, Any
import skrf as rf
from skrf.media import device

class AbstractMedia(BaseModel):
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
    type: str = Field(
        ...,
        description="Type of component"
    )

    def __init__(self, **data: Any):
        super().__init__(**data)

class R(AbstractMedia):
    r: Union[float, List[float]] = Field(
        ...,
        description="Resistance"
    )
    type: Literal['R'] = Field(
        'R',
        description="Type of component",
        frozen=True
    )

    def to_r(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        return line.resistor(self.r)

class L(AbstractMedia):
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
    type: Literal['L'] = Field(
        'L',
        description="Type of component",
        frozen=True
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

class C(AbstractMedia):
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
    type: Literal['C'] = Field(
        'C',
        description="Type of component",
        frozen=True
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

class G(AbstractMedia):
    g: Union[float, List[float]] = Field(
        ...,
        description="Conductance"
    )
    type: Literal['G'] = Field(
        'G',
        description="Type of component",
        frozen=True
    )

    def to_g(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        return line.shunt_resistor(self.g)

RLGC = Union[R, L, G, C]

class Attenuator(AbstractMedia):
    s21: Union[float, List[float]] = Field(
        ...,
        description="S21 attenuation factor"
    )
    db: Optional[bool] = Field(
        True,
        description="Whether the S21 is in dB"
    )
    d: Optional[float] = Field(
        0,
        description="Delay"
    )
    unit: Optional[str] = Field(
        'deg',
        description="Delay unit, which can be 'deg','rad','m','cm','um','in','mil','s','us','ns','ps'"
    )
    type: Literal['Attenuator'] = Field(
        'Attenuator',
        description="Type of component",
        frozen=True
    )

    def to_attenuator(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        return line.attenuator(self.s21, self.db, self.d, self.unit)

class Isolator(AbstractMedia):
    source_port: Optional[int] = Field(
        0,
        description="Port at which power can flow from, which can be 0 or 1"
    )
    type: Literal['Isolator'] = Field(
        'Isolator',
        description="Type of component",
        frozen=True
    )
    
    def to_isolator(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        if self.source_port not in [0, 1]:
            raise ValueError("source_port must be 0 or 1")
        return line.isolator(self.source_port)

class Splitter(AbstractMedia):
    nports: int = Field(
        3,
        description="Number of ports in the splitter",
        example=3
    )
    type: Literal['Splitter'] = Field(
        'Splitter',
        description="Type of component",
        frozen=True
    )    
    def to_splitter(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        return line.splitter(self.nports)

class Coupler(AbstractMedia):
    '''
    The resultant ntwk port assignment is as follows:
        * 0 - insertion
        * 1 - transmit
        * 2 - coupled
        * 3 - isolated
    '''
    db: float = Field(
        3,
        description=" the magnitude of the coupling value (in dB), sign dont matter"
    )
    deg: float = Field(
        0,
        description=" phase offset between the transmit and coupled arms. defined as : coupled arm = transmit arm +phase offset"
    )
    type: Literal['Coupler'] = Field(
        'Coupler',
        description="Type of component",
        frozen=True
    )
    @validator('db')
    def validate_db(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Coupling value must be numeric')
        return abs(float(v))
        
    @validator('deg')
    def validate_deg(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Phase offset must be an integer')
        return v % 360
    
    def to_coupler(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        line = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        coupler = device.MatchedSymmetricCoupler.from_dbdeg(db=self.db, deg=self.deg, media=line)
        return coupler.ntwk
    
Microwave = Union[Attenuator, Isolator, Splitter, Coupler]

class Port(AbstractMedia):
    name: str = Field(
        ...,
        description="Port name"
    )
    type: Literal['Port'] = Field(
        'Port',
        description="Type of component",
        frozen=True
    )

    def to_port(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        media = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        port = media.match(name=self.name)
        port._ext_attrs={'_is_circuit_port': True}
        return port

class Ground(AbstractMedia):
    name: str = Field(
        ...,
        description="Ground name"
    )
    type: Literal['Ground'] = Field(
        'Ground',
        description="Type of component",
        frozen=True
    )
    
    def to_ground(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        media = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        gnd = media.short(name=self.name)
        gnd._ext_attrs={'_is_circuit_ground': True}
        return gnd

class Open(AbstractMedia):
    name: str = Field(
        ...,
        description="Open name"
    )
    type: Literal['Open'] = Field(
        'Open',
        description="Type of component",
        frozen=True
    )
    
    def to_open(self) -> rf.Network:
        frequency = rf.Frequency.from_f(self.frequency,unit='Hz')
        z0 = [complex(real, imag) for real, imag in self.z0]
        media = rf.media.DefinedGammaZ0(frequency=frequency, z0_port=z0)
        open = media.open(name=self.name)
        open._ext_attrs={'_is_circuit_open': True}
        return open

SimComponent = Union[Port, Ground, Open]