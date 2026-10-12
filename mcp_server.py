"""MCP server for Agent Tool Call Loop Detector and Infinite Recursion Breaker."""
import sys
import json
from client import ToolCallLoopDetector


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "analyze_tool_loop",
                    "description": "Analyzes an agent's recent tool invocation trajectory to detect infinite loops, identical call repetitions, and ping-pong tool oscillations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "history": {
                                "type": "array",
                                "description": "List of recent tool calls containing 'tool_name' and 'arguments'",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tool_name": {"type": "string"},
                                        "arguments": {"type": "object"},
                                    },
                                    "required": ["tool_name"],
                                },
                            },
                            "max_identical": {
                                "type": "integer",
                                "description": "Max allowed consecutive identical tool calls before circuit break",
                                "default": 3,
                            },
                        },
                        "required": ["history"],
                    },
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        if params.get("name") == "analyze_tool_loop":
            args = params.get("arguments", {})
            history = args.get("history", [])
            max_identical = args.get("max_identical", 3)
            res = ToolCallLoopDetector.analyze_trajectory(history, max_identical=max_identical)
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
