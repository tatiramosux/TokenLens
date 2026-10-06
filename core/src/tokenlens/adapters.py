"""Provider payloads are projected in memory. Raw payloads must never be logged."""
from typing import Protocol
from .contract import new_event, number, model, finish_usage

class Adapter(Protocol):
    def normalize(self, payload: dict) -> list[dict]: ...

class CodexAdapter:
    def normalize(self, payload):
        if not isinstance(payload, dict) or payload.get("type") != "turn.completed":
            return []
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            return []
        e = new_event("codex", "codex_exec", "turn")
        for key in ("input_tokens", "output_tokens", "cached_input_tokens"):
            e["usage"][key] = number(usage.get(key))
        e["usage"]["reasoning_tokens"] = number(usage.get("reasoning_output_tokens"))
        # Completion does not prove task correctness; success remains unknown.
        return [finish_usage(e)]

class ClaudeAdapter:
    def normalize(self, payload):
        if not isinstance(payload, dict) or payload.get("type") != "result":
            return []
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            return []
        e = new_event("claude_code", "claude_result", "run")
        u = e["usage"]
        fresh = number(usage.get("input_tokens"))
        u["cached_input_tokens"] = number(usage.get("cache_read_input_tokens"))
        u["cache_creation_tokens"] = number(usage.get("cache_creation_input_tokens"))
        parts = (fresh, u["cached_input_tokens"], u["cache_creation_tokens"])
        u["input_tokens"] = sum(parts) if all(p is not None for p in parts) else None
        u["output_tokens"] = number(usage.get("output_tokens"))
        e["execution"]["duration_ms"] = number(payload.get("duration_ms"))
        models = payload.get("modelUsage", {})
        if isinstance(models, dict) and len(models) == 1:
            e["execution"]["model"] = model(next(iter(models)))
        return [finish_usage(e)]

class AntigravityAdapter:
    """No verified safe automated source: explicit capability gap, never invented usage."""
    def normalize(self, payload):
        return []

ADAPTERS = {"codex": CodexAdapter(), "claude_code": ClaudeAdapter(), "antigravity": AntigravityAdapter()}
