from datetime import datetime, timezone, timedelta
from uuid import UUID
from tokenlens.contract import new_event, finish_usage

def seed(store):
    for i in range(36):
        provider = ("codex", "claude_code", "antigravity")[i % 3]
        e = new_event(provider, "synthetic", "run", ("coding", "debugging", "research", "planning", "refactor", "other")[i % 6], ("low", "medium", "high")[i % 3], True)
        e["event_id"] = str(UUID(int=i+1))
        e["timestamp"] = (datetime.now(timezone.utc)-timedelta(hours=i*4)).isoformat()
        e["execution"].update(model=("gpt-5.5", "claude-sonnet-4-6", "gemini-2.5-pro")[i % 3], reasoning_level=("high", "medium", None)[i % 3], duration_ms=13000+i*1700, success=i % 7 != 0)
        e["usage"].update(input_tokens=2000+i*310, output_tokens=100+i*33, cached_input_tokens=i*80)
        store.put(finish_usage(e))
