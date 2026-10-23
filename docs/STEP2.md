# Step 2 — real Linux-to-STM32 communication

## Status and scope

**Firmware compiled; physical communication NOT VERIFIED.** A read-only `adb devices -l` completed outside the sandbox with no attached devices; no connected UNO Q was available for this session's test. Step 1 import/upload, Python startup, and physical LED checks remain pending. The root app's four implementation files and original Step 1 ZIP are preserved byte-for-byte. Step 2 lives in `apps/step2`, a separate valid App Lab root. Do not import the whole repository as the Step 2 app.

This milestone implements only one RPC endpoint, an MCU-owned indicator, a Python client, and diagnostics. No complete safety controller, heartbeat, dashboard, cloud dependency, or mock transport was added. Validate one real blue acknowledgement before running the additional rejection/error checks below.

## API compatibility and execution

Reviewed official sources on 2026-10-22:

- [Bridge API reference](https://docs.arduino.cc/software/app-lab/bridge/bridge-api): use `Arduino_RouterBridge.h`, `Bridge.begin`, and `provide_safe` for Arduino GPIO operations. Leave `/dev/ttyHS1` and `Serial1` exclusively to Router.
- [Python Bridge implementation](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_utils/bridge.py): `from arduino.app_utils import Bridge`; `Bridge.call(method, *params, timeout=3.0)` returns the peer's result or raises an error. The app explicitly refuses to send if the installed Python API lacks `timeout`.
- [Official Python-to-sketch example](https://github.com/arduino/app-bricks-examples/tree/main/core-and-foundational/03-bridge-basics/01-call-sketch-function-from-python): confirms RPC registration/call flow. Its Monitor call inside a `provide` callback conflicts with the current documentation warning; AEGIS avoids that pattern.
- [RouterBridge source](https://github.com/arduino-libraries/Arduino_RouterBridge): installed 0.4.3 registers `provide_safe` with a safe-dispatch tag and services it in `__loopHook` after each `loop()` return. The installed Zephyr 1.0.0 core calls that hook; inspection of the built ELF confirmed the safe-dispatch hook was included. No custom scheduling hook is needed.

The profile pins the versions actually compiled: Zephyr core 1.0.0, RouterBridge 0.4.3, RPClite 0.3.1, MsgPack 0.4.2, ArxContainer 0.7.0, ArxTypeTraits 0.3.2, and DebugLog 0.8.4. The last five libraries are Bridge dependencies, not unrelated features. No pip requirements or Bricks are added. The board-side Python/runtime versions must still be checked during deployment; locally installed C++ libraries do not prove board-side compatibility.

`loop()` returns immediately; the safe handler contains no delays, Monitor/Bridge calls, or variable-size response allocations. It validates two integers, performs bounded GPIO writes, and returns. The startup log uses `Bridge.notify(MON_WRITE_METHOD, message)`, matching the modern notification path in installed `monitor.h`, without a monitor connectivity/version handshake or reply wait. The log can be dropped when no compatible monitor is attached. Library dispatch, transport, startup, and memory allocation behavior are not hard real-time guarantees. `Bridge.begin()` and endpoint registration can block on library RPCs. There is no timeout/reconnect subsystem on the MCU in this step.

## Wire contract

Endpoint: `aegis.command(request_id: int32, command: int32)`.

| Command | Meaning |
| --- | --- |
| 0 | Set RGB LED 3 green |
| 1 | Set RGB LED 3 blue |
| Any other int32 | Reject; preserve current LED and accepted count |

A nonpositive request ID is rejected before evaluating the command. Positive IDs correlate requests and replies; reusing one does not deduplicate a request.

The MCU returns a MessagePack array serialized from `std::array<int32_t, 5>`:

```text
[protocol_version=1, request_id, status, led_code, accepted_count]
```

Status 0 means accepted, 1 means unsupported command, 2 means invalid request ID. LED code 0 is green and 1 is blue. The count starts at zero on sketch initialization, increments for each accepted request (even setting the existing color), and saturates at INT32_MAX. It is not a persistent counter or reboot identity. Incorrect argument types/arity are handled by the RPC library, not the typed application handler; a transport/protocol error is not reported as an MCU application rejection.

The client bounds arguments to int32 and validates all five reply fields, version, correlation ID, status, and accepted LED. With the MessagePack RPC envelope, two int32 arguments and this fixed response remain below 64 bytes, within the documented 256-byte transport limit. This is an encoding bound for these methods, not a promise that hostile arbitrary messages are harmless.

Python output uses `result: success`, `rejected`, `communication_error`, or `client_error`. Success/rejection includes an `ack` only after a real `Bridge.call` returns a valid response. A timeout, lost link, RPC error, or invalid response yields no invented acknowledgement. An error after starting the call has `delivery: unknown`: the MCU might already have changed its LED. There are no automatic retries. Import/signature failure before calling Bridge has `delivery: not_sent`. Missing Python modules must be fixed through the real board runtime; do not install a fake Arduino package to make the output look successful.

## Complete the remaining Step 1 physical validation first

1. Connect the UNO Q directly to the Apple Silicon Mac with a USB-C data cable. Leave headers/Qwiic empty. Open Arduino App Lab and select the actual board.
2. Import `/path/to/AEGIS/dist/AEGIS-step1.zip` using the App menu **▼ → Import App → Import from computer → Open**. Select **AEGIS** and click **Run**. Preserve any other board app before replacing its running firmware.
3. Check Start-up for build/upload success and Main/Python for `AEGIS Step 1: Linux app started; MCU startup is indicated by LED 3.`
4. Observe **LED 3 / STM-3**: three green flashes, then steady green. Observe for 10 seconds; Stop/Run and repeat. Record actual results and board/App Lab/core versions in PROGRESS.md. The detailed [Step 1 setup guide](HARDWARE_SETUP.md) also describes these steps.

No Step 1 physical acceptance result has been assumed by the Step 2 implementation.

## Package and deploy Step 2 from the Mac

```sh
cd /path/to/AEGIS
python3 scripts/package_step2.py
open -a 'Arduino App Lab'
```

The script produces `dist/AEGIS-step2.zip` with `app.yaml` at the ZIP root. It includes the separate app and three documentation files; the root Step 1 archive is untouched. Repackage after editing source files.

1. In App Lab, import that ZIP as above, open **AEGIS Step 2**, and inspect its Python/sketch files. The selected sketch profile must target UNO Q. Allow App Lab to resolve the pinned official libraries.
2. Click **Run**, inspect the build/upload logs, and keep the cable connected. This session compiled but did not upload either sketch.
3. The MCU initializes LED 3 green and registers the endpoint. If Monitor is connected during startup, the sketch console can show `AEGIS MCU: aegis.command ready; protocol=1`. A missing Monitor line alone is not an RPC failure. The accepted counter in every reply is also an MCU diagnostic. An explicitly failed registration sets red; a startup handshake that never returns may leave green.
4. Python's entry point logs `AEGIS Step 2: calling aegis.command id=1 command=1 once` and sends one real request. It then stays under `App.run()` lifecycle control without periodic calls.
5. Require **both** Python `result: success` with ACK version 1, request ID 1, status 0, LED blue, accepted count at least 1 **and physical LED 3 changing to blue**. Save the actual output; expected values in this document are not recorded hardware observations. An ACK confirms the handler issued GPIO writes; observation verifies the light.
6. If an initial readiness race or timeout occurs, inspect logs before retrying manually. A timeout does not prove the command was rejected. Never replace `Bridge.call` with a literal reply to pass the test.

Stop here until that first physical acknowledgement succeeds. The checks below test only the remaining requirements of Step 2.

## Repeat, rejection, and communication-error checks

The simplest supported repeat is App Lab **Stop → Run**, which re-executes the startup request. For a deliberate green/blue sequence in App Lab, change only the `REQUEST_ID` and `COMMAND` constants in `python/main.py`, save, and Run. Use these pairs in order, verifying the actual JSON each time:

| Request ID / command | Required outcome |
| --- | --- |
| 101 / 0 | MCU ACK success, green LED |
| 102 / 1 | MCU ACK success, blue LED |
| 103 / 99 | MCU rejection `unsupported_command`; no LED change |
| 0 / 0 | MCU rejection `invalid_request_id`; no LED change |

App Lab Run may reload/reset firmware, so accepted counts may restart and the initial green setup can reappear. For no-reset rejection/state-retention tests, use the repeated-script procedure below, keeping the same running sketch. Restore `COMMAND = 1` and `REQUEST_ID = 1` after an editor-based demonstration, or reimport the unchanged ZIP. The validated JSON and physical LED are the evidence.

For a genuine communication failure, first preserve/export any modified app. Use the unchanged root **AEGIS Step 1** sketch (which registers no `aegis.command`) together with the Step 2 Python client in a temporary App Lab copy, then Run that copy. Require a missing-method RPC error or timeout and **no `ack` or success result**. This deliberately mismatched hardware app is a negative test, not a successful MCU exchange. Restore **AEGIS Step 2** afterward. Do not stop the Router service or touch its UART to induce failure.

The script `python/rpc_demo.py` also sends exactly one command and exits 0 for success, 2 for rejection, 3 for communication failure, or 4 for invalid local input. CLI `--help` and offline checks can run on the Mac; a real command must run in the board's app Python environment. It must not be mistaken for macOS-to-MCU communication.

### Repeated script execution in the actual App Lab runtime

After the first physical ACK succeeds, the following uses App Lab's supported `python/main.py` entry point to invoke the demonstration script four times within one MCU run. It needs no SSH, Docker path assumptions, or host Arduino package.

1. Keep **AEGIS Step 2** open. Preserve its original `python/main.py` (also contained in the generated ZIP).
2. Temporarily replace **only its board-side `python/main.py`** in App Lab with the code below; retain the other two Python modules and Step 2 sketch. This wrapper supplies command-line arguments to the real demo; it never supplies a response.
3. Click **Run** once, watch LED 3, and capture the four JSON results. There is no sketch reset between these four script invocations. Require green then blue; both rejections must preserve blue and the accepted count from request 102. Counts for 101 and 102 must differ by exactly one.
4. Stop/Run repeats the entire hardware demonstration. Restore the original entry point afterward by reimporting `AEGIS-step2.zip` using a fresh app name if the importer reports a conflict; preserve any edits you need before replacing a board app. The repository source is unaffected by these board-side editor changes.

```python
import sys
import time
from arduino.app_utils import App
from rpc_demo import main as run_command

for command, request_id, expected_exit in (
    ("green", 101, 0),
    ("blue", 102, 0),
    ("reject", 103, 2),
    ("green", 0, 2),
):
    sys.argv = ["rpc_demo.py", command, "--request-id", str(request_id)]
    actual_exit = run_command()
    if actual_exit != expected_exit:
        print("AEGIS demo stopped: unexpected result; inspect JSON above", flush=True)
        break
    time.sleep(2)  # Linux-only observation pause; the MCU keeps servicing RPC.
App.run()
```

Advanced shell execution is possible with `docker exec` in the running app's Python container, but this board's container path/interpreter has not been inspected, so no guessed container command is supplied. Arduino App CLI does not provide an arbitrary `app exec` command. The managed-entry-point procedure above is the documented deployment path and exact repeatable test for this milestone.

## Local checks

```sh
cd /path/to/AEGIS
python3 -m unittest discover -s tests -v
python3 apps/step2/python/rpc_demo.py --help
AEGIS_CLI='/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli'
"$AEGIS_CLI" compile --profile default --warnings all \
  --build-path /tmp/aegis-step2-profile-build apps/step2/sketch
```

The profile build needs permission to write Arduino CLI's isolated cache. Its full pinned build passed in this session after cache population, as did the installed-core build. Offline tests use explicitly synthetic parser fixtures only; they neither replace Bridge nor count as hardware validation. The host-only command below is expected to exit 3 with `ModuleNotFoundError` on this Mac, proving only that no local Arduino runtime is installed:

```sh
python3 apps/step2/python/rpc_demo.py blue --request-id 101
```

Record actual Step 1 and Step 2 hardware results in PROGRESS.md before advancing. No Step 3 work is included.
