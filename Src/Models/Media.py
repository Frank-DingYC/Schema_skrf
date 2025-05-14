from pydantic.v1 import Field
from typing import List, Union, Optional
from .Component import AbstractMedia
from tidy3d.components.types import 

class RectangularWaveguide(AbstractMedia):
    m: int = Field(
        1,
        title="Horizontal Mode Index"
        description="mode index along 'a' direction"
    )
    n: int = Field(
        0,
        title="Vertical Mode Index",
        description="mode index along 'b' direction"
    )
    mode_type: Optional[str] = Field(
        None,
        title="Mode Type",
        description="mode type, which can be 'TE' or 'TM'"
    )
    a: Optional[float] = Field(
        None,
        title="Length",
        description="length of waveguide, in meter"
    )
    b: Optional[float] = Field(
        None,
        title="Width",
        description="width of waveguide, in meter"
    )
    ep_r: Union[float, List[float]] = Field(
        1,
        description="relative permittivity of waveguide material"
    )
    mu_r: Union[float, List[float]] = Field(
        1,
        description="relative permeability of waveguide material"
    )