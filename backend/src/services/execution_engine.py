"""
MiniNodes Execution Engine

Walks the workflow graph node by node, starting from a trigger node.
Passes output of each node as input to connected nodes.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from src.nodes.base import registry
from src.database import SessionLocal
from src.models.execution import Execution, ExecutionStatus


class ExecutionEngine:

    async def start(self):
        pass  # Future: start schedule runners here

    async def stop(self):
        pass

    async def run(
        self,
        workflow_id: str,
        graph: dict,
        trigger: str = "manual",
        input_data: Any = None,
    ) -> str:
        execution_id = str(uuid.uuid4())
        db = SessionLocal()

        execution = Execution(
            id=execution_id,
            workflow_id=workflow_id,
            status=ExecutionStatus.running,
            trigger=trigger,
            input_data=input_data,
            node_results={},
        )
        db.add(execution)
        db.commit()

        try:
            node_results = await self._execute_graph(graph, input_data)
            execution.node_results = node_results
            execution.status = ExecutionStatus.success
        except Exception as e:
            execution.status = ExecutionStatus.error
            execution.error = str(e)
        finally:
            execution.finished_at = datetime.now(timezone.utc)
            db.commit()
            db.close()

        return execution_id

    async def _execute_graph(self, graph: dict, initial_data: Any) -> dict:
        nodes = {n["id"]: n for n in graph.get("nodes", [])}
        edges = graph.get("edges", [])

        # Build adjacency: source_node_id -> list of (target_node_id, source_handle, target_handle)
        adjacency: dict[str, list[tuple[str, str, str]]] = {}
        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            src_handle = edge.get("sourceHandle", "out")
            tgt_handle = edge.get("targetHandle", "in")
            adjacency.setdefault(src, []).append((tgt, src_handle, tgt_handle))

        # Find trigger node (no incoming edges)
        targets = {e["target"] for e in edges}
        trigger_nodes = [nid for nid in nodes if nid not in targets]

        node_outputs: dict[str, Any] = {}
        results: dict[str, dict] = {}

        async def execute_node(node_id: str, input_data: Any):
            node_def = nodes[node_id]
            node_type = node_def["type"]
            config = node_def.get("data", {}).get("config", {})

            handler = registry.get(node_type)
            if not handler:
                raise ValueError(f"Unknown node type: {node_type}")

            try:
                output = await handler.execute(config, input_data)
                node_outputs[node_id] = output
                results[node_id] = {"output": output, "error": None}
            except Exception as e:
                results[node_id] = {"output": None, "error": str(e)}
                raise

            # Propagate to connected nodes
            for (tgt_id, src_handle, tgt_handle) in adjacency.get(node_id, []):
                # If/Else routing
                if isinstance(output, dict) and "_branch" in output:
                    if src_handle != output["_branch"]:
                        continue
                    next_input = output["data"]
                else:
                    next_input = output

                await execute_node(tgt_id, next_input)

        for trigger_id in trigger_nodes:
            await execute_node(trigger_id, initial_data)

        return results


engine = ExecutionEngine()
