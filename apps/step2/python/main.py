"""App Lab entry point: request one real MCU acknowledgement, then stay alive."""

import json

from arduino.app_utils import App
from rpc_client import send_command

COMMAND = 1  # 0 green, 1 blue, any other int32 requests MCU rejection.
REQUEST_ID = 1


if __name__ == "__main__":
    print(f"AEGIS Step 2: calling aegis.command id={REQUEST_ID} command={COMMAND} once", flush=True)
    print(json.dumps(send_command(command=COMMAND, request_id=REQUEST_ID), sort_keys=True), flush=True)
    # No automatic retries or periodic commands. A timeout leaves delivery unknown.
    App.run()
