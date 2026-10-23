"""Linux application shell; Step 1 sends no commands to the MCU."""

from arduino.app_utils import App


if __name__ == "__main__":
    print("AEGIS Step 1: Linux app started; MCU startup is indicated by LED 3.", flush=True)
    App.run()
