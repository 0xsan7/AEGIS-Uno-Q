#include <Arduino.h>
#include <Arduino_RouterBridge.h>
#include <array>
#include <cstdint>
#include <limits>

// ACK: [protocol_version, request_id, status, led_code, accepted_count].
// Status: 0 accepted, 1 unsupported command, 2 invalid request ID.
// Command / LED: 0 green, 1 blue. This is a communication demo, not a policy.
using Acknowledgement = std::array<int32_t, 5>;
static int32_t ledCode = 0;
static int32_t acceptedCount = 0;

Acknowledgement handleCommand(int32_t requestId, int32_t command) {
  int32_t status = 0;
  if (requestId <= 0) {
    status = 2;
  } else if (command != 0 && command != 1) {
    status = 1;
  } else {
    // provide_safe runs here on the sketch context, not the RPC thread.
    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);
    digitalWrite(command == 0 ? LED3_G : LED3_B, LOW);
    ledCode = command;
    if (acceptedCount < std::numeric_limits<int32_t>::max()) {
      ++acceptedCount;
    }
  }
  // No delay, Monitor/Bridge calls, or variable-size allocations in handler.
  return {1, requestId, status, ledCode, acceptedCount};
}

void setup() {
  pinMode(LED3_R, OUTPUT);
  digitalWrite(LED3_R, HIGH);
  pinMode(LED3_G, OUTPUT);
  digitalWrite(LED3_G, HIGH);
  pinMode(LED3_B, OUTPUT);
  digitalWrite(LED3_B, HIGH);
  digitalWrite(LED3_G, LOW);

  // Official library startup handshakes may block if Router is unavailable.
  // Never open Serial1 or the Router UART ourselves.
  if (!Bridge.begin()) {
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_R, LOW);
    return;
  }
  const bool registered = Bridge.provide_safe("aegis.command", handleCommand);
  if (!registered) {
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_R, LOW);
  }
  // Best-effort startup log through the same Router notification used by
  // Monitor.write in RouterBridge 0.4.3. No mon/connected or version RPC:
  // absence of a monitor must not prevent the safe-handler loop from starting.
  const String startupMessage = registered ? "AEGIS MCU: aegis.command ready; protocol=1\n"
                                          : "AEGIS MCU: endpoint registration failed\n";
  Bridge.notify(MON_WRITE_METHOD, startupMessage);
}

void loop() {
  // Return immediately. RouterBridge's __loopHook services provide_safe calls.
}
