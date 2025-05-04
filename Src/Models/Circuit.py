from pydantic import BaseModel
from typing import Dict, List, Union, Tuple
import Src.Models.Network as Network
import skrf as rf

ConnectionType = Union[
    Tuple[str, int],  # (network_name, port_number)
    List[Tuple[str, int]]  # [(network_name, port_number)]
]

class Circuit(BaseModel):
    networks: Dict[str, Network.Network]
    connections: List[List[ConnectionType]]

    @classmethod
    def from_circuit(cls, circuit: rf.Circuit) -> 'Circuit':
        networks = {ntw.name: Network.Network.from_network(ntw) for ntw in circuit.networks_list}
        connections = [[(conn[0].name, conn[1]) for conn in conn_list] for conn_list in circuit.connections]
        return cls(networks=networks, connections=connections)

    def to_circuit(self) -> rf.Circuit:
        network_objects = {name: ntw.to_network() for name, ntw in self.networks.items()}
        return rf.Circuit(
            connections=[
                [(network_objects[conn[0]], conn[1]) for conn in conn_list] 
                for conn_list in self.connections
            ]
        )