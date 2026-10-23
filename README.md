# AEGIS

**The Hardware That Doesn't Trust Its Own OS.** A dual-processor safety proof of concept for Arduino UNO Q: Linux will propose operations; the STM32U585 will independently validate them and own the controlled outputs.

**Step 1 only:** an Arduino App Lab foundation and MCU startup indicator. LED 3 flashes green three times, then stays green. This demonstrates sketch startup, not a safety system. Validation, safe-state enforcement, heartbeat, and dashboard are not implemented.

The repository root is the App Lab app:

```text
app.yaml
python/main.py       # Linux lifecycle shell; no hardware commands
sketch/sketch.ino    # MCU-owned onboard LED 3
sketch/sketch.yaml   # UNO Q / Zephyr 1.0.0; pinned RouterBridge dependencies
docs/
```

Use an UNO Q and a USB-C data cable; no additional electronics or cloud service is needed. Python uses App Lab's supplied `arduino.app_utils`; there are no pip requirements or Bricks to add.

- [Hardware setup and exact Mac deployment steps](docs/HARDWARE_SETUP.md)
- [Architecture, responsibility boundary, and threat model](docs/ARCHITECTURE.md)
- [Verification results and next milestone](docs/PROGRESS.md)

Firmware compilation passed on an Apple Silicon Mac and, after pinning the required libraries, in a compile-only check on the UNO Q. App Lab import succeeded; successful upload/run and physical LED behavior remain **NOT VERIFIED**. A privileged Linux attacker able to replace/reset MCU firmware is outside the intended application-level guarantee; processor separation alone does not secure that path.

Step 2 is a separate App Lab app under [`apps/step2`](apps/step2). It adds one real Bridge command with a bounded MCU acknowledgement and an LED color change. The root Step 1 application is preserved. See [Step 2 deployment and physical acceptance](docs/STEP2.md); physical RPC success remains **NOT VERIFIED** until tested on the UNO Q.
