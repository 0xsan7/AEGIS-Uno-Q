#include <Arduino.h>

// UNO Q MCU-owned RGB LED 3: LOW = on, HIGH = off.
// A startup indication only; this does not assert safety or continuing health.
void setup() {
  pinMode(LED3_R, OUTPUT);
  digitalWrite(LED3_R, HIGH);
  pinMode(LED3_G, OUTPUT);
  digitalWrite(LED3_G, HIGH);
  pinMode(LED3_B, OUTPUT);
  digitalWrite(LED3_B, HIGH);

  delay(500);
  for (int flash = 0; flash < 3; ++flash) {
    digitalWrite(LED3_G, LOW);
    delay(250);
    digitalWrite(LED3_G, HIGH);
    delay(250);
  }
  digitalWrite(LED3_G, LOW);
}

void loop() {
  // Yield without RPC, a heartbeat, or a safety policy in Step 1.
  delay(1000);
}
