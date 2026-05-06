import httpx
import json
from typing import Any
from src.nodes.base import BaseNode, registry


class WebhookTriggerNode(BaseNode):
    type = "core.webhook_trigger"
    label = "Webhook"
    description = "Triggers the workflow when a webhook is received"
    color = "#10b981"
    icon = "ri-webhook-line"
    inputs = []
    outputs = [{"id": "out", "label": "Output"}]
    fields = [
        {
            "key": "custom_path",
            "label": "Custom Path (optional)",
            "type": "text",
            "placeholder": "my-webhook  →  /webhook/my-webhook",
            "default": "",
        },
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        return input_data


class ManualTriggerNode(BaseNode):
    type = "core.manual_trigger"
    label = "Manual Trigger"
    description = "Manually start the workflow"
    color = "#10b981"
    icon = "ri-play-circle-line"
    inputs = []
    outputs = [{"id": "out", "label": "Output"}]
    fields = [
        {"key": "payload", "label": "Test Payload (JSON)", "type": "json",
         "default": "{}", "placeholder": "{\"hello\": \"world\"}"},
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        payload = config.get("payload", {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}
        return payload if payload else input_data


class OutputNode(BaseNode):
    type = "core.output"
    label = "Output"
    description = "Marks the final output of the workflow"
    color = "#0ea5e9"
    icon = "ri-download-line"
    inputs = [{"id": "in", "label": "Input"}]
    outputs = []
    fields = [
        {"key": "label", "label": "Output Label", "type": "text",
         "placeholder": "Result", "default": "Result"},
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        return {
            "_output": True,
            "label": config.get("label", "Result"),
            "data": input_data,
        }


class HttpRequestNode(BaseNode):
    type = "core.http_request"
    label = "HTTP Request"
    description = "Make an HTTP request to any URL"
    color = "#6366f1"
    icon = "ri-global-line"
    inputs = [{"id": "in", "label": "Input"}]
    outputs = [{"id": "out", "label": "Output"}, {"id": "error", "label": "Error"}]
    fields = [
        {"key": "method", "label": "Method", "type": "select",
         "options": ["GET", "POST", "PUT", "PATCH", "DELETE"], "default": "GET"},
        {"key": "url", "label": "URL", "type": "text", "placeholder": "https://api.example.com"},
        {"key": "headers", "label": "Headers", "type": "json", "default": "{}"},
        {"key": "body", "label": "Body", "type": "json", "default": "{}"},
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        method = config.get("method", "GET")
        url = config.get("url", "")
        headers = config.get("headers", {})
        body = config.get("body", {})

        if isinstance(headers, str):
            headers = json.loads(headers)
        if isinstance(body, str):
            body = json.loads(body) if body else {}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method != "GET" else None,
            )
            try:
                data = response.json()
            except Exception:
                data = response.text

            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": data,
            }


class IfElseNode(BaseNode):
    type = "core.if_else"
    label = "If / Else"
    description = "Route data based on a condition"
    color = "#f59e0b"
    icon = "ri-git-branch-line"
    inputs = [{"id": "in", "label": "Input"}]
    outputs = [{"id": "true", "label": "True"}, {"id": "false", "label": "False"}]
    fields = [
        {"key": "field", "label": "Field (dot notation)", "type": "text", "placeholder": "body.status"},
        {"key": "operator", "label": "Operator", "type": "select",
         "options": ["equals", "not_equals", "contains", "greater_than", "less_than", "exists"]},
        {"key": "value", "label": "Value", "type": "text", "placeholder": "200"},
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        field = config.get("field", "")
        operator = config.get("operator", "equals")
        value = config.get("value", "")

        actual = input_data
        for key in field.split("."):
            if isinstance(actual, dict):
                actual = actual.get(key)
            else:
                actual = None
                break

        result = False
        if operator == "equals":
            result = str(actual) == str(value)
        elif operator == "not_equals":
            result = str(actual) != str(value)
        elif operator == "contains":
            result = str(value) in str(actual or "")
        elif operator == "greater_than":
            try:
                result = float(actual) > float(value)
            except Exception:
                result = False
        elif operator == "less_than":
            try:
                result = float(actual) < float(value)
            except Exception:
                result = False
        elif operator == "exists":
            result = actual is not None

        return {"_branch": "true" if result else "false", "data": input_data}


class TransformNode(BaseNode):
    type = "core.transform"
    label = "Transform"
    description = "Reshape or extract data using a template"
    color = "#8b5cf6"
    icon = "ri-shuffle-line"
    inputs = [{"id": "in", "label": "Input"}]
    outputs = [{"id": "out", "label": "Output"}]
    fields = [
        {"key": "template", "label": "Output Template (JSON)", "type": "json",
         "placeholder": '{"orderId": "{{body.id}}", "total": "{{body.total_price}}"}'},
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        template = config.get("template", "{}")
        if isinstance(template, str):
            try:
                template = json.loads(template)
            except Exception:
                return input_data

        def resolve(val):
            if isinstance(val, str) and "{{" in val:
                key = val.strip("{} ")
                result = input_data
                for part in key.split("."):
                    if isinstance(result, dict):
                        result = result.get(part)
                    else:
                        result = None
                return result
            elif isinstance(val, dict):
                return {k: resolve(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [resolve(i) for i in val]
            return val

        return resolve(template)


class SetVariableNode(BaseNode):
    type = "core.set_variable"
    label = "Set Variable"
    description = "Add or overwrite fields on the data object"
    color = "#ec4899"
    icon = "ri-pencil-line"
    inputs = [{"id": "in", "label": "Input"}]
    outputs = [{"id": "out", "label": "Output"}]
    fields = [
        {"key": "assignments", "label": "Assignments (JSON)", "type": "json",
         "placeholder": '{"myField": "hello", "count": 42}'},
    ]

    async def execute(self, config: dict, input_data: Any) -> Any:
        assignments = config.get("assignments", {})
        if isinstance(assignments, str):
            try:
                assignments = json.loads(assignments)
            except Exception:
                assignments = {}

        if isinstance(input_data, dict):
            return {**input_data, **assignments}
        return assignments


class MergeNode(BaseNode):
    type = "core.merge"
    label = "Merge"
    description = "Merge two inputs into one object"
    color = "#14b8a6"
    icon = "ri-merge-cells-horizontal"
    inputs = [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]
    outputs = [{"id": "out", "label": "Output"}]
    fields = []

    async def execute(self, config: dict, input_data: Any) -> Any:
        if isinstance(input_data, dict) and "a" in input_data and "b" in input_data:
            a = input_data["a"] or {}
            b = input_data["b"] or {}
            if isinstance(a, dict) and isinstance(b, dict):
                return {**a, **b}
        return input_data


# Register all core nodes
for node_class in [
    WebhookTriggerNode,
    ManualTriggerNode,
    OutputNode,
    HttpRequestNode,
    IfElseNode,
    TransformNode,
    SetVariableNode,
    MergeNode,
]:
    registry.register(node_class())