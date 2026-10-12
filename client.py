"""Agent Tool Call Loop Detector and Infinite Recursion Breaker.
100% Python Standard Library.
"""

from typing import List, Dict, Any, Optional
import hashlib
import json


class ToolCallLoopDetector:
    """Analyzes autonomous agent tool execution trajectories to detect infinite retry loops,
    ping-pong oscillations between complementary tools, and repetitive semantic stagnation."""

    DEFAULT_WINDOW_SIZE = 10
    MAX_IDENTICAL_CALLS_THRESHOLD = 3
    MAX_CYCLE_REPETITIONS_THRESHOLD = 2

    @staticmethod
    def _hash_call(tool_name: str, arguments: Any) -> str:
        """Computes a deterministic hash for a tool name and normalized arguments."""
        try:
            arg_str = json.dumps(arguments, sort_keys=True, default=str)
        except Exception:
            arg_str = str(arguments)
        combined = f"{tool_name}::{arg_str}".encode("utf-8")
        return hashlib.md5(combined).hexdigest()

    @classmethod
    def analyze_trajectory(
        cls,
        history: List[Dict[str, Any]],
        window_size: int = DEFAULT_WINDOW_SIZE,
        max_identical: int = MAX_IDENTICAL_CALLS_THRESHOLD,
        max_cycles: int = MAX_CYCLE_REPETITIONS_THRESHOLD,
    ) -> Dict[str, Any]:
        """Inspects an array of tool execution records.
        Each record should contain at least:
            - 'tool_name' (str)
            - 'arguments' (dict or str)
        """
        if not history:
            return {
                "status": "PASS",
                "circuit_break": False,
                "loop_detected": False,
                "reason": "Trajectory is empty.",
                "consecutive_identical_count": 0,
                "cycle_detected": None,
                "recommended_action": "CONTINUE",
            }

        # Focus on the recent sliding window
        window = history[-window_size:]
        hashes = [cls._hash_call(item.get("tool_name", ""), item.get("arguments", {})) for item in window]
        tool_names = [item.get("tool_name", "") for item in window]

        # 1. Check for immediate consecutive identical tool calls
        consecutive_identical = 1
        last_hash = hashes[-1]
        for h in reversed(hashes[:-1]):
            if h == last_hash:
                consecutive_identical += 1
            else:
                break

        if consecutive_identical >= max_identical:
            last_tool = tool_names[-1]
            return {
                "status": "CIRCUIT_BREAKER_TRIGGERED",
                "circuit_break": True,
                "loop_detected": True,
                "loop_type": "IDENTICAL_RETRY_LOOP",
                "consecutive_identical_count": consecutive_identical,
                "offending_tool": last_tool,
                "reason": f"Tool '{last_tool}' was executed {consecutive_identical} times consecutively with identical arguments.",
                "recommended_action": "ABORT_OR_INJECT_SYSTEM_HINT",
                "system_hint": (
                    f"Warning: Tool '{last_tool}' is failing to produce forward progress with the current parameters. "
                    "Stop repeating this tool call. Attempt an alternative approach, modify input arguments, or report blockers directly."
                ),
            }

        # 2. Check for alternating cycle loops (e.g. A -> B -> A -> B or A -> B -> C -> A -> B -> C)
        n = len(hashes)
        for pattern_len in range(2, min(n // 2 + 1, 5)):
            pattern = hashes[-pattern_len:]
            repeats = 1
            idx = n - pattern_len * 2
            while idx >= 0:
                if hashes[idx : idx + pattern_len] == pattern:
                    repeats += 1
                    idx -= pattern_len
                else:
                    break

            if repeats >= max_cycles:
                cycle_tools = tool_names[-pattern_len:]
                return {
                    "status": "CIRCUIT_BREAKER_TRIGGERED",
                    "circuit_break": True,
                    "loop_detected": True,
                    "loop_type": "ALTERNATING_CYCLE_LOOP",
                    "cycle_pattern": cycle_tools,
                    "cycle_repetitions": repeats,
                    "reason": f"Cyclic tool oscillation detected across pattern {' -> '.join(cycle_tools)} repeated {repeats} times.",
                    "recommended_action": "BREAK_OSCILLATION",
                    "system_hint": (
                        f"Warning: Detected cyclic oscillation between tools ({' -> '.join(cycle_tools)}). "
                        "Synthesize current partial observations and formulate a consolidated final answer instead of continuing tool execution."
                    ),
                }

        return {
            "status": "PASS",
            "circuit_break": False,
            "loop_detected": False,
            "reason": "Trajectory exhibits progressive tool selection without infinite recursion.",
            "consecutive_identical_count": consecutive_identical,
            "recommended_action": "CONTINUE",
        }
