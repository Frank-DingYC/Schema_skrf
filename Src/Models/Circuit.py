from pydantic import BaseModel, Field
import skrf as rf
import numpy as np
from typing import List, Optional, Dict, Any

# Pydantic model for scikit-rf's Circuit object
class Circuit(BaseModel):
    name: Optional[str] = Field(
        None,
        description="Circuit name",
        example="test_circuit"
    )
    networks: Dict[str, Network] = Field(
        ...,
        description="Dictionary of Network objects in the circuit, keyed by name",
    )
    connections: List[List[Any]] = Field(
        ...,
        description="List of connections between ports (e.g., [[('ntw1', 0), ('ntw2', 0)]])",
        example=[[["ntw1", 0], ["ntw2", 0]]]
    )
    connection_list: Optional[List[List[Any]]] = Field(
        None,
        description="Detailed list of all connections in the circuit",
    )
    edges: Optional[List[Any]] = Field(
        None,
        description="List of all edges represented in Scikit-rf's Circuit",
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            np.ndarray: lambda v: v.tolist(),
            complex: lambda v: [v.real, v.imag]
        }

    @classmethod
    def from_circuit(cls, circuit: rf.Circuit) -> 'Circuit':
        networks = {
            ntw.name or f"ntw_{i}": Network.from_network(ntw)
            for i, ntw in enumerate(circuit.networks)
        }
        connection_list = [
            [[conn.ntw.name or f"ntw_{i}", conn.port] for conn in conn_group]
            for i, conn_group in enumerate(circuit.connection_list)
        ]
        edges = circuit.edges
        connections = [
            [[conn[0].name or f"ntw_{i}", conn[1]] for conn in conn_list]
            for i, conn_list in enumerate(circuit.connections)
        ]
        return cls(
            name=circuit.name,
            networks=networks,
            connections=connections,
            connection_list=connection_list,
            edges=edges
        )

    def to_circuit(self) -> rf.Circuit:
        network_objects = {
            name: schema.to_network() for name, schema in self.networks.items()
        }
        connections = [
            [(network_objects[conn[0][0]], conn[0][1]) for conn in conn_list]
            for conn_list in self.connections
        ]
        circuit = rf.Circuit(connections, name=self.name)
        circuit.connection_list = self.connection_list
        circuit.edges = self.edges
        return circuit

    @classmethod
    def from_json(cls, json_data: Dict) -> 'Circuit':
        json_data['networks'] = {
            name: Network(**data) for name, data in json_data['networks'].items()
        }
        return cls(**json_data)