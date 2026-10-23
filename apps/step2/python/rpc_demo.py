"""One command per invocation. Execute using the UNO Q app's Python runtime."""

import argparse
import json

from rpc_client import send_command

EXIT_CODES = {"success": 0, "rejected": 2, "communication_error": 3, "client_error": 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("green", "blue", "reject"))
    parser.add_argument("--request-id", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()
    command = {"green": 0, "blue": 1, "reject": 99}[args.command]
    print(f"AEGIS Linux: calling aegis.command id={args.request_id} command={command}", flush=True)
    result = send_command(command, args.request_id, args.timeout)
    print(json.dumps(result, sort_keys=True), flush=True)
    return EXIT_CODES[result["result"]]


if __name__ == "__main__":
    raise SystemExit(main())
