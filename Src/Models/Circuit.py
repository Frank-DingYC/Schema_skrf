from pydantic.v1 import BaseModel, Field, validator
from typing import Dict, List, Union, Tuple, Any
import Src.Models.Network as Network
import Src.Models.Component as Component
import skrf as rf

NetworkType = Union[Network.Network, Component.RLGC, Component.Microwave, Component.SimComponent]
ConnectionType = Union[
    Tuple[str, int],  # (network_name, port_number)
    List[Tuple[str, int]]  # [(network_name, port_number)]
]

class Circuit(BaseModel):
    networks: Dict[str, NetworkType] = Field(
        ...,
        description="Dictionary of networks/components keyed by their names"
    )
    connections: List[List[ConnectionType]] = Field(
        ...,
        description="List of connection groups, where each group is a list of (network_name, port) tuples"
    )

    def __init__(self, **data: Any):
        print("Original networks:")
        for name, net in data['networks'].items():
            print(f"{name}: {type(net)}")
        super().__init__(**data)
        print("\nAfter Pydantic validation:")
        for name, net in self.networks.items():
            print(f"{name}: {type(net)}")

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
            if net.frequency != freq_points:
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
            for ntw in circuit.networks_list
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
            if isinstance(net, Network.Network):
                network_objects[name] = net.to_network()
            elif isinstance(net, Component.RLGC):
                # Handle RLGC components
                if isinstance(net, Component.R):
                    network_objects[name] = net.to_r()
                elif isinstance(net, Component.L):
                    network_objects[name] = net.to_l()
                elif isinstance(net, Component.G):
                    network_objects[name] = net.to_g()
                elif isinstance(net, Component.C):
                    network_objects[name] = net.to_c()
            elif isinstance(net, Component.Microwave):
                # Handle Microwave components
                if isinstance(net, Component.Attenuator):
                    network_objects[name] = net.to_attenuator()
                elif isinstance(net, Component.Isolator):
                    network_objects[name] = net.to_isolator()
                elif isinstance(net, Component.Splitter):
                    network_objects[name] = net.to_splitter()
                elif isinstance(net, Component.Coupler):
                    network_objects[name] = net.to_coupler()
            elif isinstance(net, Component.SimComponent):
                # Handle Simulation components
                if isinstance(net, Component.Port):
                    network_objects[name] = net.to_port()
                elif isinstance(net, Component.Ground):
                    network_objects[name] = net.to_ground()
                elif isinstance(net, Component.Open):
                    network_objects[name] = net.to_open()
            else:
                raise ValueError(f"Unsupported network type for '{name}'")
            
            # Set network name while preserving _ext_attrs
            ext_attrs = getattr(network_objects[name], '_ext_attrs', {})
            network_objects[name].name = name
            if ext_attrs:
                network_objects[name]._ext_attrs = ext_attrs

        # Create connections list
        connections = [
            [(network_objects[conn[0]], conn[1]) for conn in conn_list]
            for conn_list in self.connections
        ]

        # Create circuit and set networks_list
        circuit = rf.Circuit(connections=connections)
        circuit.networks_list = list(network_objects.values())
        return circuit