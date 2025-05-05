from pydantic.v1 import Field
from typing import List, Union, Optional
from .Component import AbstractMedia

class RectangularWaveguide(AbstractMedia):
    m: int = Field(
        1,
        description="mode index along 'a' direction"
    )
    n: int = Field(
        0,
        description="mode index along 'b' direction"
    )
    mode_type: Optional[str] = Field(
        None,
        description="mode type, which can be 'TE' or 'TM'"
    )
    a: Optional[float] = Field(
        None,
        description="width of waveguide, in meter"
    )
    b: Optional[float] = Field(
        None,
        description="length of waveguide, in meter"
    )
    ep_r: Union[float, List[float]] = Field(
        1,
        description="relative permittivity of waveguide material"
    )
    mu_r: Union[float, List[float]] = Field(
        1,
        description="relative permeability of waveguide material"
    )