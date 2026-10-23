# AEGIS

An experimental project exploring MCU-side validation of Linux-originated commands on the **Arduino UNO Q**.

The intended design places output control and validation on the STM32U585, while Linux proposes operations through Arduino Router/Bridge. The current implementation establishes the application structure, an MCU startup indicator, and a separate interprocessor communication demo. The safety policy is not implemented yet.

> **Development prototype.** Firmware builds and offline tests have passed. Successful deployment, physical LED behavior, and a real on-board RPC exchange remain unverified. AEGIS is not a validated or certified safety controller.

## Current status

| Milestone | Implementation | Verification |
| --- | --- | --- |
| Step 1 — MCU startup indicator | LED 3 flashes green three times, then remains green | Profile compilation passed on the UNO Q; physical behavior and Linux app startup pending |
| Step 2 — Linux-to-MCU command | One Bridge request, structured acknowledgement, green/blue commands, and explicit rejection | Firmware compilation and 10 offline tests passed; physical RPC and LED checks pending |
| Step 3 — MCU safety policy | Not implemented | Not tested |

The LED descriptions above are expected behavior from the code, not recorded hardware observations. See [verification evidence and remaining work](docs/PROGRESS.md) for details.

## How it is organized

The repository contains two independent Arduino App Lab applications:

```text
AEGIS/
├── app.yaml                 # Step 1 application manifest
├── python/main.py           # Step 1 Linux lifecycle entry point
├── sketch/                  # Step 1 MCU sketch and pinned dependencies
├── apps/step2/              # Separate Bridge/RPC demonstration app
├── docs/                    # Architecture, setup, and verification records
├── scripts/package_step2.py # Step 2 App Lab archive builder
└── tests/                   # Offline Python protocol checks
```

Step 1 sends no application commands to the MCU. Step 2 uses `aegis.command(request_id, command)` to request green or blue on MCU LED 3 and validate the returned acknowledgement. It does not implement a safety policy, heartbeat, authentication, or replay protection.

## Hardware and setup

- Arduino UNO Q and a USB-C data cable.
- Arduino App Lab; the recorded development version is 1.0.0.
- Arduino Q Boards / Zephyr core 1.0.0 and the library versions pinned in each app's `sketch/sketch.yaml`.

These demos use onboard LEDs and need no external electronics. Python uses the App Lab-provided `arduino.app_utils` runtime; no extra pip packages or Bricks are declared. Initial dependency downloads require internet access.

Start with the [Step 1 hardware setup guide](docs/HARDWARE_SETUP.md). Complete Step 1 hardware acceptance before following the [Step 2 deployment and RPC verification procedure](docs/STEP2.md). App Lab **Run** builds and uploads MCU firmware; review the selected application before running it.

Deployment ZIPs and build artifacts are not tracked. Generate a fresh archive from the current source using the documented packaging steps. Previously generated local archives may contain older dependency metadata.

## Offline checks

From the repository root, run:

```sh
python3 -B -m unittest discover -s tests -v
```

These tests check acknowledgement parsing and argument validation using explicitly synthetic fixtures. They do not communicate with an Arduino or establish hardware acceptance.

## Design boundaries

The future policy is intended to validate requests within the MCU application. Linux still participates in firmware deployment and reset, so processor separation alone does not protect against an attacker who can replace MCU firmware. A steady LED is not proof of continuing execution or system health.

Read the [architecture and threat model](docs/ARCHITECTURE.md) for the processor responsibilities, assumptions, and limits.
