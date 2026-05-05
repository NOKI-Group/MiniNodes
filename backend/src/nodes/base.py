from abc import ABC, abstractmethod
from typing import Any


class BaseNode(ABC):
    """Every MiniNodes node inherits from this."""

    # Unique identifier, e.g. "core.http_request"
    type: str
    label: str
    description: str = ""
    color: str = "#6366f1"
    icon: str = "ri-node-tree"

    # Input/output port definitions
    inputs: list[dict] = [{"id": "in", "label": "Input"}]
    outputs: list[dict] = [{"id": "out", "label": "Output"}]

    # Config fields shown in the node sidebar
    fields: list[dict] = []

    @abstractmethod
    async def execute(self, config: dict, input_data: Any) -> Any:
        """Run the node. Return output data."""
        ...

    def to_definition(self) -> dict:
        return {
            "type": self.type,
            "label": self.label,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "fields": self.fields,
        }


class NodeRegistry:
    _nodes: dict[str, BaseNode] = {}

    @classmethod
    def register(cls, node: BaseNode):
        cls._nodes[node.type] = node

    @classmethod
    def get(cls, node_type: str) -> BaseNode | None:
        return cls._nodes.get(node_type)

    @classmethod
    def all(cls) -> list[dict]:
        return [n.to_definition() for n in cls._nodes.values()]


registry = NodeRegistry()
