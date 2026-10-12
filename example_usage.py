"""Example usage for Agent Tool Call Loop Detector."""
from client import ToolCallLoopDetector

if __name__ == "__main__":
    # Test identical retry loop
    looping_history = [
        {"tool_name": "fetch_api", "arguments": {"endpoint": "/users", "page": 1}},
        {"tool_name": "fetch_api", "arguments": {"endpoint": "/users", "page": 1}},
        {"tool_name": "fetch_api", "arguments": {"endpoint": "/users", "page": 1}},
    ]
    res = ToolCallLoopDetector.analyze_trajectory(looping_history)
    print("Circuit Break Triggered:", res["circuit_break"])
    print("Loop Type:", res.get("loop_type"))
    print("Reason:", res["reason"])
    print("Action:", res["recommended_action"])

    # Test alternating oscillation loop
    oscillation_history = [
        {"tool_name": "search_db", "arguments": {"query": "auth"}},
        {"tool_name": "read_docs", "arguments": {"doc_id": "auth_spec"}},
        {"tool_name": "search_db", "arguments": {"query": "auth"}},
        {"tool_name": "read_docs", "arguments": {"doc_id": "auth_spec"}},
    ]
    res_osc = ToolCallLoopDetector.analyze_trajectory(oscillation_history)
    print("\nOscillation Break Triggered:", res_osc["circuit_break"])
    print("Loop Type:", res_osc.get("loop_type"))
    print("Cycle Pattern:", res_osc.get("cycle_pattern"))
