from pydantic.v1 import Field, validator
from tidy3d.components.base import Tidy3dBaseModel
from tidy3d.components.types import ComplexNumber
from typing import Dict, List, Union, Tuple, Any, Optional
import Src.Models.Network as Network
import Src.Models.Component as Component
import skrf as rf
import numpy as np

NetworkType = Union[Network.Network, Component.RLGC, Component.Microwave, Component.SimComponent]
ConnectionType = Union[
    Tuple[str, int],  # (network_name, port_number)
    List[Tuple[str, int]]  # [(network_name, port_number)]
]

class Circuit(Tidy3dBaseModel):
    """Circuit component"""
    networks: Dict[str, NetworkType] = Field(
        ...,
        title="Networks",
        description="Dictionary of networks/components keyed by their names",
        example={
            'r1': {
                'type': 'R',
                'r': 50,
                'frequency': [1e9],
                'z0': {'real': 50, 'imag': 0}
            }
        }
    )
    connections: List[List[ConnectionType]] = Field(
        ...,
        title="Connections",
        description="List of connection groups, where each group is a list of (network_name, port) tuples",
        example=[[('ntw1', 0), ('r1', 0)]]
    )
    type: str = Field(
        'Circuit',
        title="Type",
        description="Type of the model",
        example="Circuit"
    )
    attrs: Dict[str, Any] = Field(
        default_factory=dict,
        title="Attributes",
        description="Additional attributes",
        example={"note": "Example circuit"}
    )

    def __init__(self, **data: Any):
        super().__init__(**data)

    @validator('networks')
    def validate_networks(cls, v):
        """Validate that all networks have compatible frequency points"""
        if not v:
            return v
        
        # Get frequency points from first network
        first_net = next(iter(v.values()))
        freq_points = first_net.frequency
        
        # Check all networks have same frequency points
        for name, net in v.items():
            if not np.array_equal(net.frequency, freq_points):
                raise ValueError(f"Network '{name}' has incompatible frequency points")
        return v

    @validator('connections')
    def validate_connections(cls, v, values):
        """Validate that all connections reference valid networks"""
        if 'networks' not in values:
            return v
        
        networks = values['networks']
        for group in v:
            for conn in group:
                if isinstance(conn, tuple):
                    name = conn[0]
                    if name not in networks:
                        raise ValueError(f"Network '{name}' not found in networks")
                else:
                    for name, _ in conn:
                        if name not in networks:
                            raise ValueError(f"Network '{name}' not found in networks")
        return v

    @classmethod
    def from_circuit(cls, circuit: rf.Circuit) -> 'Circuit':
        """Create Circuit from scikit-rf Circuit object"""
        networks = {
            ntw.name: Network.Network.from_network(ntw) 
            for ntw in circuit.networks_list()
        }
        connections = [
            [(conn[0].name, conn[1]) for conn in conn_list] 
            for conn_list in circuit.connections
        ]
        return cls(networks=networks, connections=connections)

    def to_circuit(self) -> rf.Circuit:
        """Convert to scikit-rf Circuit object"""
        # Convert all networks/components to rf.Network objects
        network_objects = {}
        for name, net in self.networks.items():
            if isinstance(net, NetworkType):
                temp_network = net.to_network()
                temp_network.name = name
                network_objects[name] = temp_network
            else:
                raise ValueError(f"Network '{name}' is not a valid network type")
        connections = [[(network_objects[conn[0]], conn[1]) for conn in conn_list] for conn_list in self.connections]
        circuit = rf.Circuit(connections)
        return circuit

if __name__ == "__main__":
    import json
    with open('circuit.json','w') as f:
        circuit_schema = Circuit.schema()
        json.dump(circuit_schema, f, indent=4)