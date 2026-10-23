# AEGIS Step 2 — one real Bridge acknowledgement

This app runs on the UNO Q. Python sends `aegis.command(1, 1)` once on startup. The STM32 sets MCU-owned LED 3 blue and returns a compact acknowledgement through Arduino Router/Bridge. A successful build alone does not establish a working hardware link.

Import this app's ZIP into Arduino App Lab, open **AEGIS Step 2**, and click **Run**. The expected physical result is green at MCU setup, then blue after a successful request. The Python console must show `result: success` with request ID 1 and a blue LED acknowledgement. This is an expected outcome, not an observation from the development session.

The root repository app and `dist/AEGIS-step1.zip` retain Step 1 for its outstanding physical checks. Validate Step 1 before recording Step 2 acceptance. See `docs/STEP2.md` in the repository or deployment archive for the complete procedure and error meanings.

The repeatable client is `python/rpc_demo.py`: commands `green`, `blue`, and `reject`; optional `--request-id` and `--timeout`. Run it using the actual app Python environment on the UNO Q, not macOS system Python. The app itself issues no periodic requests or retries. Steady color proves neither continuing health nor safety.
