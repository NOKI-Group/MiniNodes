# MiniNodes

A lightweight, embeddable node-based workflow engine. MIT licensed.
## Info

MiniNodes is designed to be more user friendly, lighter and easier to extend than NodeRed or n8n.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vue Flow, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Infrastructure | Docker, Docker Compose |

## Getting Started

```bash
git clone https://github.com/NOKI-Studios/MiniNodes.git
cd mininodes
docker compose up -d
```

- Frontend: http://localhost:5174
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Core Nodes

| Node | Description |
|---|---|
| Webhook Trigger | Start a workflow from an incoming HTTP request |
| HTTP Request | Call any external API |
| If / Else | Branch based on a condition |
| Transform | Reshape JSON data using a template |
| Set Variable | Add or overwrite fields |
| Merge | Combine two inputs into one |

## Plugin System

Nodes are registered via the `NodeRegistry`. To add a node:

```python
from src.nodes.base import BaseNode, registry

class MyNode(BaseNode):
    type = "myplugin.my_node"
    label = "My Node"
    fields = [
        {"key": "url", "label": "URL", "type": "text"}
    ]

    async def execute(self, config: dict, input_data) -> any:
        return {"result": "hello"}

registry.register(MyNode())
```

## License

MIT
