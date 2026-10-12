# genpark-agent-tool-call-loop-detector-and-infinite-recursion-breaker-skill

Detects recursive tool-call loops, identical argument oscillations, and agent trajectory deadlocks with automated circuit breaker heuristics.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities
- **Consecutive Identical Call Detection**: Deterministically hashes tool names and normalized argument structures to detect stuck retry loops.
- **Alternating Pattern Circuit Breaking**: Detects multi-step cyclic oscillations (e.g. `Tool A -> Tool B -> Tool A -> Tool B`) across sliding trajectory windows.
- **Actionable Recovery Guidance**: Emits structured system prompts and remediation guidance for agent context injection when loops occur.
- **Zero-Dependency Fast Execution**: Sub-millisecond execution overhead using standard library hashing and evaluation.

## Architecture

```
[Agent Trajectory Invocations]
             │
             ▼
┌──────────────────────────────────────────────┐
│  ToolCallLoopDetector                        │
│  ├─ Hash Normalizer (MD5)                    │
│  ├─ Consecutive Retry Evaluator              │
│  └─ N-gram Cyclic Oscillation Matcher        │
└──────────────────────────────────────────────┘
             │
      ┌──────┴──────────────────────┐
      ▼                             ▼
[PASS: Progressive]     [CIRCUIT_BREAKER_TRIGGERED]
                        ├─ System Injected Hint
                        └─ Recommended Action (ABORT/BREAK)
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `analyze_tool_loop`: Evaluates an array of recent tool invocations and returns circuit breaker status and remediation advice.

## Quickstart

```python
from client import ToolCallLoopDetector

history = [
    {"tool_name": "search_db", "arguments": {"query": "auth"}},
    {"tool_name": "search_db", "arguments": {"query": "auth"}},
    {"tool_name": "search_db", "arguments": {"query": "auth"}},
]

result = ToolCallLoopDetector.analyze_trajectory(history)
print(result["status"])  # "CIRCUIT_BREAKER_TRIGGERED"
print(result["system_hint"])
```
