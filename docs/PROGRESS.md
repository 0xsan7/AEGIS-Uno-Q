# Progress

## 2026-10-24 — Pause checkpoint for public source backup

Status: **Step 1 profile compilation PASS; Step 1 hardware acceptance NOT VERIFIED; Step 2 hardware acceptance NOT VERIFIED. No Step 3 implementation.**

The entries below are historical records. This checkpoint supersedes their statements about absent USB hardware, an empty Step 1 library list, and blocked Step 1 profile compilation.

- USB/ADB access to a physical UNO Q was established. The existing Step 1 archive imported successfully through the installed board-side Arduino App CLI. Device identifiers, Wi-Fi details, and local network addresses are omitted from this public record.
- Initial deployment failed before upload because package-host DNS resolution was refused. Subsequent read-only HTTPS checks confirmed DNS, TCP 443, verified TLS, and HTTP 200 for the Arduino package index. No network configuration was changed.
- A later deployment resolved the pinned Zephyr 1.0.0 core and tools but compilation failed on the core's RouterBridge stub. RouterBridge 0.4.3 already existed globally and in caches; the Step 1 profile's empty library list excluded it from the isolated build.
- With user approval, only the local and imported Step 1 `sketch/sketch.yaml` profiles were updated to pin RouterBridge 0.4.3, RPClite 0.3.1, MsgPack 0.4.2, ArxContainer 0.7.0, ArxTypeTraits 0.3.2, and DebugLog 0.8.4. Application logic and Step 2 source remained unchanged.
- The board-side compile-only command used `arduino-cli compile --profile default --board-options wait_linux_boot=app --warnings all --build-path /tmp/aegis-step1-profile-20261023 <imported-app>/sketch` and exited 0. No upload flag or app start was used after this dependency correction.
- Compiler report: **75,256 / 786,432 bytes program storage (9%); 30,636 / 262,144 bytes global RAM (11%); 231,508 bytes remaining for local variables**. These are compiler-reported figures, not full runtime resource guarantees.
- Local and board-side profile SHA-256 matched: `46f0c79abfd9e04755661d3a878d9688cbd51fa35bb958ddf62c92209bf6d2ef`. The Step 1 sketch remained `4c5e9100cc38775d6de51e9570fc0ad8839a1669fc364fb568d1575802ed40ca`.
- The original local Step 1 ZIP was preserved and still contains the older profile. It is a generated artifact excluded from Git; regenerate from the current checkout before any future import. Step 2's generated archive is also excluded and can be recreated using `scripts/package_step2.py`.

Resume with explicit approval for Step 1 upload/run, then collect successful upload and Linux startup logs and the user's observation of exactly three green flashes followed by at least ten seconds of steady green on MCU LED 3. Do not mark hardware PASS from compilation alone. Step 2 must wait for Step 1 acceptance and separate authorization to resume it.

---

## 2026-10-22 — Step 2: interprocessor communication

Status: **implementation and local checks complete; physical success condition NOT VERIFIED. Stop after Step 2.**

### Baseline and physical verification gate

- Read ARCHITECTURE.md and this progress record before implementation. Step 1 import/upload, Python startup, physical LED behavior, and repeat-run acceptance remain **NOT VERIFIED**. The user confirmed compilation/static validation, not hardware integration.
- The four root implementation files (`app.yaml`, `python/main.py`, `sketch/sketch.ino`, `sketch/sketch.yaml`) and original `dist/AEGIS-step1.zip` were hash-checked before/after and preserved byte-for-byte. Step 2 is a separate app under `apps/step2`; root Step 1 remains available for the outstanding checklist.
- Read-only host inspection found App Lab installed but not running. macOS USB inventory reported a service error. A sandboxed ADB attempt could not start its daemon; a subsequent permitted `adb devices -l` outside the sandbox completed successfully and returned an empty attached-device list. No USB board was available through ADB in this session; network-only connectivity was not established. No board was flashed, reset, or claimed tested.

### Implemented

- MCU `aegis.command(int32 request_id, int32 command)` registered through official `Bridge.provide_safe`. Commands 0/1 set MCU RGB LED 3 green/blue. Invalid IDs and unsupported commands return explicit rejection without updating the LED/count.
- Fixed-size structured reply `[1, request_id, status, led_code, accepted_count]`. Short integer messages, no UART access, no waits or nested Bridge/Monitor calls in the handler, and an immediately returning sketch loop.
- Python uses only real `arduino.app_utils.Bridge.call`, checks finite-timeout API support, sends once, validates the reply, and distinguishes accepted/rejected/local-invalid/communication-error outcomes. A timeout means delivery unknown. No mock transport, fallback ACK, periodic retry, or simulated hardware path exists.
- One startup request in App Lab's Python entry point; repeatable `rpc_demo.py` with exit codes and one command per invocation. MCU best-effort startup notification to Router's Monitor method and accepted-count reply; Python request/result logging. No safety policy controller, heartbeat, or dashboard.
- Added `docs/STEP2.md`, app README, packaging script, and offline contract tests. Updated root README and architecture with the separate Step 2 scope. Nothing committed or pushed.

### API and dependency compatibility

Reviewed current official Bridge API, Python implementation, examples, and installed MCU source. Local tested versions are core `arduino:zephyr` 1.0.0; RouterBridge 0.4.3; RPClite 0.3.1; MsgPack 0.4.2; ArxContainer 0.7.0; ArxTypeTraits 0.3.2; DebugLog 0.8.4. All C++ dependencies are pinned in the Step 2 profile. No extra Python packages or Bricks are requested.

Installed `provide_safe` executes from RouterBridge's `__loopHook`, called by the Zephyr sketch core. Both `Bridge.begin` and endpoint registration return booleans in the installed API. Startup Bridge handshakes can block in this library; no bounded-startup/recovery claim is made. Review caught an unnecessary synchronous Monitor startup dependency; it was replaced with the library's `mon/write` notification path, without waiting for monitor connectivity/version replies. The official Python API supports `timeout`; the actual board-side Python installation remains uninspected and must pass the client compatibility check on hardware.

### Actual verification results

| Check | Result | Evidence / scope |
| --- | --- | --- |
| Step 1 implementation/archive preservation | **PASS** | SHA-256 equality for four root app files and original ZIP before/after development. Documentation was extended separately. |
| Step 2 App Lab layout / YAML / Python syntax | **PASS (static)** | Independent app root contains required four paths and three Python modules; manifest has no Bricks/ports; YAML parses and pins UNO Q/core/libraries. Python AST parsing passed. |
| Firmware with installed core/libraries | **PASS** | CLI 1.3.1 `--fqbn arduino:zephyr:unoq --warnings all`, byte-identical `.ino` copy without profile, exit 0. Actual RouterBridge source appears in compilation database; no fake headers/stubs. |
| Full pinned profile compilation | **PASS** | `compile --profile default --warnings all apps/step2/sketch`, exit 0. Initial sandbox cache-write failure was resolved by allowing CLI cache population; the subsequent full profile build compiled the repository source and declared library versions. No upload flag used. |
| Compiler report (both final builds) | **PASS** | 87,884 / 786,432 bytes program storage (11%); globals 35,452 / 262,144 bytes (13%), leaving 226,692 bytes. Toolchain-reported values after removing the synchronous Monitor startup dependency. |
| Safe dispatch linked into firmware | **PASS (static)** | ARM ELF symbol/disassembly inspection found `handleCommand`, `BridgeClass::update_safe`, and the nonempty RouterBridge `__loopHook`. This does not prove on-board scheduling. |
| Offline protocol tests | **PASS: 10 tests** | `python3 -m unittest discover -s tests -v`. Explicit synthetic decoder fixtures and local argument validation only; no Arduino module/Bridge mocks. These are not MCU responses. |
| Demo CLI / absent local runtime | **PASS (negative local check)** | `--help` works. Mac command `rpc_demo.py blue --request-id 101` exits 3 with `communication_error`, `ModuleNotFoundError`, `delivery: not_sent`, and no ACK. This is not a physical communication-error test. |
| Step 2 package | **PASS** | ZIP CRC and exact 10-file membership/source-byte checks passed; separate app at ZIP root plus three documentation files. Step 1, caches, binaries, and Git metadata excluded. |
| Step 1 hardware acceptance | **NOT VERIFIED** | Follow Step 1 gate in STEP2.md / HARDWARE_SETUP.md before recording integration success. |
| Board-side Python API/runtime compatibility | **NOT VERIFIED** | Current official API inspected; actual UNO Q runtime not accessed. |
| First physical Linux→STM32 ACK + LED | **NOT VERIFIED** | Requires actual App Lab Run, valid MCU reply, and observed LED 3 blue. No physical success result was fabricated. |
| Repeated physical commands/rejection/link failure | **NOT VERIFIED** | Run only after first physical ACK; exact procedures in STEP2.md. |

Step 2 compiled sketch SHA-256: `624a429324de35c0a95faaeb6f17eaa7140f5467470fe2c7aa4a377777ba6151`.

### Remaining hardware actions and next milestone

Import/run the preserved Step 1 app and record its physical checks first. Then import/run **AEGIS Step 2**, capture the actual request/ACK JSON and observe MCU LED 3 change green→blue. Only after that first real acknowledgement, exercise repeat/rejection and missing-endpoint checks. Record board variant, App Lab/core/Bridge/Python runtime versions, actual outputs, colors, and pass/fail here.

The next development milestone requires a separate instruction after hardware acceptance: define and implement a bounded MCU-side safety policy. No further controller features were added before obtaining the first physical acknowledgement.

---

The following Step 1 record is retained as historical evidence; its physical checks are still outstanding.

## 2026-10-22 — Step 1: architecture and application foundation

Status: **implementation complete; hardware acceptance pending. Stop at Step 1.**

### Repository and environment inspection

- The supplied workspace was empty. Git initially discovered an unrelated ancestor repository; no changes were made there.
- Cloned `https://github.com/0xsan7/AEGIS-Uno-Q.git` into this workspace. The remote was empty (no commits or project instructions). No existing user source files were overwritten.
- Host: Darwin arm64 / Apple Silicon. Python 3.14 and PyYAML 6.0.3 were already available for static checks; PyYAML is not an application dependency.
- Arduino App Lab 1.0.0 and Arduino IDE are installed. Arduino CLI is not on PATH but IDE bundles version 1.3.1 (`08ff7e2b`). Globally installed core: `arduino:zephyr` 1.0.0.
- A read-only USB inventory attempt produced a macOS USB-service error and did not confirm a board. No hardware connection or board identity is asserted.

### Completed work

- Read the official UNO Q user manual, Arduino App specification, Bridge API reference, MCU blink app, and Python-to-sketch Bridge example. Sources are linked in ARCHITECTURE.md; Arduino's raw documentation sources were used where the documentation website returned an empty rendered page.
- Defined Linux/MCU responsibilities, conditional trust assumptions, runtime threats, and limits around Linux-controlled firmware programming, reset, shared power, and MCU integrity.
- Added root `app.yaml`, `python/main.py`, `sketch/sketch.ino`, and `sketch/sketch.yaml`. Selected the documented onboard LED 3 APIs; no invented RGB library or external hardware.
- Added a startup-only MCU sequence: 500 ms off, three 250 ms green flashes separated by 250 ms off, then steady green. No application Bridge calls, validation policy, heartbeat, dashboard, or safe-state enforcement.
- Added `.gitignore`, README, architecture, setup instructions, and this progress record. Python uses only the App Lab-supplied lifecycle framework; no extra Bricks, pip dependencies, or sketch libraries.
- Prepared `dist/AEGIS-step1.zip` as an ignored deployment artifact. Git remains uncommitted; nothing was pushed.

### Actual verification results

| Check | Result | Evidence / scope |
| --- | --- | --- |
| Official app structure | **PASS (static)** | Root name `AEGIS` is allowed; exact mandatory filenames are present, sketch basename matches folder, metadata fields have appropriate types, no ports/Bricks requested. Compared with official app spec and blink template. |
| YAML parsing and sketch profile | **PASS (static)** | Both YAML documents parsed; default profile exists and selects `arduino:zephyr:unoq`, platform `arduino:zephyr (1.0.0)`, and empty libraries. This is not App Lab runtime validation. |
| Python syntax | **PASS** | Parsed `python/main.py` using Python AST; no runtime import substitution or simulated board was used. |
| Official LED symbols | **PASS (source inspection)** | UNO Q manual and installed core `variants/arduino_uno_q_stm32u585xx/variant.h` confirm LED3_R/G/B. Core GPIO implementation and manual confirm LOW-on behavior. |
| Repository profile compilation | **BLOCKED / NOT VERIFIED** | CLI attempted isolated profile installation and could not create a temporary directory under `~/Library/Arduino15/tmp` within the sandbox. This is not a source compilation error. |
| Firmware compilation with installed core | **PASS** | CLI 1.3.1, `--fqbn arduino:zephyr:unoq`, installed Zephyr 1.0.0; exit code 0. Byte-identical source copied into `/tmp/aegis-step1-installed/sketch` without the profile file. No mocked headers or stubs. |
| Compiler size report | **PASS** | Program storage: 75,256 / 786,432 bytes (9%). Globals: 30,636 / 262,144 bytes (11%); 231,508 bytes remaining. These are toolchain-reported figures, not total board resource guarantees. |
| Archive integrity | **PASS** | ZIP CRC check passed; exactly nine source/documentation files, each byte-identical to the working tree; no Git metadata, caches, or binaries. |
| Board-side Python/App Lab lifecycle | **NOT VERIFIED** | No board-side execution performed; the Mac syntax check does not test `arduino.app_utils`. |
| App Lab import/build/upload | **NOT VERIFIED** | Documented actions supplied; no device was flashed. |
| Physical LED behavior / re-run | **NOT VERIFIED** | Requires the manual checklist in HARDWARE_SETUP.md. No hardware observation has been fabricated. |

Compiled sketch SHA-256: `4c5e9100cc38775d6de51e9570fc0ad8839a1669fc364fb568d1575802ed40ca`.

### Blockers and next milestone

The remaining Step 1 acceptance work is physical: connect the UNO Q, import/run AEGIS, check board-side dependency compatibility and the LED pattern, then record the results here. The sandbox prevented the isolated profile build, but the available installed-core compile passed. Hardware/runtime results must not be inferred from that compile.

After hardware acceptance and a separate instruction to proceed, the next milestone is to define a small bounded command contract and implement/test MCU-side validation and explicit safe-state behavior using onboard resources. Resolve Bridge callback threading against the installed library first. Heartbeat/liveness behavior and a dashboard remain future work; no Step 2 implementation was started.
