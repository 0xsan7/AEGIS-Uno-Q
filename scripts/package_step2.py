"""Package the Step 2 app only; preserve the Step 1 root app and archive."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "step2"
FILES = (
    "app.yaml", "README.md", "python/main.py", "python/rpc_client.py",
    "python/rpc_demo.py", "sketch/sketch.ino", "sketch/sketch.yaml",
)


def main():
    destination = ROOT / "dist" / "AEGIS-step2.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(APP / name, name)
        for name in ("STEP2.md", "PROGRESS.md", "HARDWARE_SETUP.md"):
            archive.write(ROOT / "docs" / name, "docs/" + name)
    with ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("archive CRC validation failed")
    print(destination)


if __name__ == "__main__":
    main()
