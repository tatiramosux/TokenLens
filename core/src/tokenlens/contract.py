"""Closed schema: reject unknown fields; never interpolate invalid input in errors."""
import json
from datetime import datetime, timezone
from importlib.resources import files
from uuid import uuid4
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = json.loads(files("tokenlens").joinpath("event.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
CATEGORIES = ("unknown", "coding", "debugging", "refactor", "research", "planning", "other")
COMPLEXITIES = ("unknown", "low", "medium", "high")
# Explicit public catalog: arbitrary/custom model names never enter telemetry.
MODELS = set(SCHEMA["properties"]["execution"]["properties"]["model"]["enum"])

class InvalidEvent(ValueError):
    pass

def validate(event):
    try:
        invalid = next(VALIDATOR.iter_errors(event), None) is not None
    except (TypeError, ValueError, RecursionError):
        invalid = True
    if invalid:
        raise InvalidEvent("Evento rejeitado pelo contrato de privacidade.")
    u = event["usage"]
    if u["total_tokens"] is not None:
        if u["input_tokens"] is None or u["output_tokens"] is None or u["total_tokens"] != u["input_tokens"] + u["output_tokens"]:
            raise InvalidEvent("Contagem de tokens inconsistente.")
    if u["cached_input_tokens"] is not None and u["input_tokens"] is not None and u["cached_input_tokens"] > u["input_tokens"]:
        raise InvalidEvent("Contagem de cache inconsistente.")
    if u["reasoning_tokens"] is not None and u["output_tokens"] is not None and u["reasoning_tokens"] > u["output_tokens"]:
        raise InvalidEvent("Contagem de raciocinio inconsistente.")
    if u["input_tokens"] is not None:
        parts = [u[k] for k in ("cached_input_tokens", "cache_creation_tokens") if u[k] is not None]
        if sum(parts) > u["input_tokens"]:
            raise InvalidEvent("Contagem de cache inconsistente.")
    return event

def number(value):
    return value if type(value) is int and 0 <= value <= 10**12 else None

def model(value):
    return value if isinstance(value, str) and value in MODELS else None

def new_event(provider, source="manual", scope="request", category="unknown", complexity="unknown", synthetic=False):
    return {
        "schema_version": "1.0", "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider, "source": source, "scope": scope, "synthetic": synthetic,
        "task": {"category": category, "complexity": complexity, "classification_source": "manual" if category != "unknown" or complexity != "unknown" else "unknown"},
        "execution": {"model": None, "reasoning_level": None, "duration_ms": None, "success": None},
        "usage": {"input_tokens": None, "output_tokens": None, "cached_input_tokens": None, "cache_creation_tokens": None, "reasoning_tokens": None, "total_tokens": None},
        "assessment": {"model_fit": "unknown"},
    }

def finish_usage(event):
    u = event["usage"]
    if u["input_tokens"] is not None and u["output_tokens"] is not None:
        u["total_tokens"] = u["input_tokens"] + u["output_tokens"]
    return validate(event)
