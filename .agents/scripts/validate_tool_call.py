import json
import sys


def main():
    try:
        # Read the event payload passed via stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            # Fallback to allowing if no stdin data is provided
            print(json.dumps({"allow_tool": True, "decision": "allow"}))
            return

        payload = json.loads(input_data)

        # Extract command line argument
        command_line = ""

        tool_call = payload.get("toolCall", {})
        if tool_call:
            args = tool_call.get("args", {})
            if args:
                command_line = args.get("CommandLine", "")

        # Blocklist of destructive commands/terms
        blocklist = ["rm -rf /", "mkfs"]

        normalized_command = command_line.lower().strip()

        is_blocked = False
        reason = ""
        for term in blocklist:
            if term in normalized_command:
                is_blocked = True
                reason = f"Execution blocked: Destructive command pattern '{term}' is not allowed."
                break

        if is_blocked:
            response = {
                "allow_tool": False,
                "decision": "deny",
                "deny_reason": reason,
                "reason": reason,
            }
        else:
            response = {"allow_tool": True, "decision": "allow"}

        # Output decision JSON to stdout
        print(json.dumps(response))

    except Exception as e:
        # Block by default in case of error
        print(
            json.dumps(
                {
                    "allow_tool": False,
                    "decision": "deny",
                    "deny_reason": f"Validation script execution error: {e!s}",
                }
            )
        )


if __name__ == "__main__":
    main()
