# Hardware setup — Apple Silicon Mac

## Equipment and prerequisites

Use only an Arduino UNO Q and a USB-C **data** cable connected directly to the Mac. Leave the headers and Qwiic connector empty. No external LED, resistor, shield, debugger, monitor, or USB hub is needed for this PC-hosted workflow. The [UNO Q manual](https://docs.arduino.cc/tutorials/uno-q/user-manual/) documents USB-C power at 5 V / 3 A; use an appropriate port/cable and resolve unstable power before testing.

Arduino App Lab is already installed at `/Applications/Arduino App Lab.app` on this Mac (reported version 1.0.0). If installing elsewhere, choose the macOS Apple Silicon download from [Arduino software](https://www.arduino.cc/en/software/). Complete App Lab's board connection/setup prompts, including board credentials and any required software provisioning. Internet may be needed for initial package/image downloads; AEGIS has no cloud service, account integration, or runtime network dependency of its own. macOS does not need Linux udev rules.

The local compiler used Arduino CLI 1.3.1 and `arduino:zephyr` 1.0.0. The app profile pins that core version, RouterBridge 0.4.3, RPClite 0.3.1, MsgPack 0.4.2, ArxContainer 0.7.0, ArxTypeTraits 0.3.2, and DebugLog 0.8.4. These libraries are required by the core even for Step 1. Profile builds exclude global library installations. App Lab's board-side runtime and installed core must be checked during the first deployment; a Mac compilation does not establish board-side compatibility.

## Prepare the app archive

Replace `/path/to/AEGIS` below with your checkout location. Run in Terminal. This uses Python's standard library and packages only the nine project files, with `app.yaml` at the ZIP root. It excludes Git metadata, credentials, caches, and build products. Re-run after editing project files.

```sh
cd /path/to/AEGIS
python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

files = [
    'app.yaml', 'python/main.py', 'sketch/sketch.ino', 'sketch/sketch.yaml',
    'README.md', '.gitignore', 'docs/ARCHITECTURE.md',
    'docs/PROGRESS.md', 'docs/HARDWARE_SETUP.md',
]
Path('dist').mkdir(exist_ok=True)
with ZipFile('dist/AEGIS-step1.zip', 'w', ZIP_DEFLATED) as archive:
    for name in files:
        archive.write(name, name)
print(Path('dist/AEGIS-step1.zip').resolve())
PY
open -a 'Arduino App Lab'
```

## Deploy with App Lab

1. Connect the UNO Q by USB-C, allow it to boot, and select its USB connection in App Lab. Complete initial setup if prompted. Preserve/export any existing board app you want to keep before replacing the running sketch.
2. Follow the official [Import App workflow](https://docs.arduino.cc/software/app-lab/apps/manage-apps/): open an app, select the **▼** menu beside its name, then **Import App → Import from computer**. Select `/path/to/AEGIS/dist/AEGIS-step1.zip` and click **Open**. If the app list exposes Import directly, that reaches the same operation. If there is no existing user app to open, **My Apps → Create new app +** can create a temporary app to access the menu.
3. Open the imported **AEGIS** app. Check that the Python and sketch editors contain the repository code, and the sketch profile targets UNO Q / Zephyr 1.0.0. Imports make a board-side copy; subsequent local edits require another import or a matching editor update. Preserve existing apps if a naming conflict is reported.
4. Click **Run** at the top right. This builds and uploads the MCU sketch and starts Python on the board. Confirm replacement of a running app only when you intend to replace it. Keep the cable connected through compilation/upload.
5. Check **Console / Start-up** for successful build/upload, and the Python console for `AEGIS Step 1: Linux app started; MCU startup is indicated by LED 3.` No MCU console message is expected: this sketch does not use Monitor or Serial.
6. Watch **RGB LED 3 / STM-3**, not Linux LEDs 1/2 or the blue matrix. After sketch setup begins: about 500 ms off, three green flashes, then steady green. Linux boot and deployment add time before this sequence.

These actions follow the current official documentation; this session did not execute an App Lab import or upload. Older App Lab versions may expose different menus; update via Arduino's supported process if Import is unavailable. Do not reflash the Linux image merely to upload this sketch.

## Repeat the local firmware compile

The normal profile command is:

```sh
cd /path/to/AEGIS
AEGIS_CLI='/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli'
"$AEGIS_CLI" compile --profile default --build-path /tmp/aegis-step1-profile-build sketch
```

Profile builds use an isolated dependency cache even when the core and libraries are globally installed. Earlier cache and dependency failures are historical; the corrected profile subsequently passed a compile-only check on the UNO Q with `wait_linux_boot=app`. See PROGRESS.md for the exact result. No firmware upload followed that successful compilation.

The following equivalent-source build passed using this Mac's installed 1.0.0 core. The temporary copy intentionally excludes `sketch.yaml` to avoid profile-cache downloads; the repository profile is not modified. This is compile-only and does not flash a board.

```sh
cd /path/to/AEGIS
AEGIS_CLI='/Applications/Arduino IDE.app/Contents/Resources/app/lib/backend/resources/arduino-cli'
"$AEGIS_CLI" core list
AEGIS_BUILD_ROOT="$(mktemp -d /tmp/aegis-step1.XXXXXX)"
mkdir -p "$AEGIS_BUILD_ROOT/sketch"
cp sketch/sketch.ino "$AEGIS_BUILD_ROOT/sketch/sketch.ino"
"$AEGIS_CLI" compile --fqbn arduino:zephyr:unoq \
  --build-path "$AEGIS_BUILD_ROOT/build" "$AEGIS_BUILD_ROOT/sketch"
cmp sketch/sketch.ino "$AEGIS_BUILD_ROOT/sketch/sketch.ino"
```

## Manual LED acceptance checklist

- [ ] App Lab reports successful MCU build/upload; the Python console has the startup line and no traceback.
- [ ] LED 3 flashes green **three times**, then stays green. Red and blue remain off after initialization; ignore brief GPIO/boot transients.
- [ ] Observe for 10 seconds: green stays steady, with no repeating blink cycle. This is not a heartbeat.
- [ ] Stop and run AEGIS again in App Lab; observe the startup sequence again. Stop/reset behavior by itself is not a safety test.
- [ ] Record date, board variant, App Lab/core versions, and pass/fail in `docs/PROGRESS.md`.

If the LED does not match, first confirm the selected board/app, upload logs, and LED number. The original Blink example's repeating red light indicates different firmware. An expected green LED alone cannot verify Python, RPC, policy enforcement, continued MCU execution, or cold-start independence. This step does not configure Run at startup; after a power cycle, select AEGIS and click Run again.
