"""Real Bridge client. No mock transport or synthetic acknowledgement path."""

import inspect

METHOD = "aegis.command"
INT32_MAX = 2_147_483_647
INT32_MIN = -2_147_483_648


def decode_ack(reply, request_id, command):
    """Validate the compact MCU reply before reporting an accepted operation."""
    if not isinstance(reply, (list, tuple)) or len(reply) != 5:
        raise ValueError("expected a five-integer MCU acknowledgement")
    if any(type(value) is not int or not INT32_MIN <= value <= INT32_MAX for value in reply):
        raise ValueError("acknowledgement fields must be signed 32-bit integers")
    version, echoed_id, status, led, count = reply
    if version != 1 or echoed_id != request_id or led not in (0, 1) or count < 0:
        raise ValueError("invalid protocol version, request ID, LED, or count")
    expected = 2 if request_id <= 0 else (1 if command not in (0, 1) else 0)
    if status != expected:
        raise ValueError("MCU status does not match the request contract")
    if status == 0 and (led != command or count == 0):
        raise ValueError("accepted reply does not confirm the requested LED")
    return {
        "version": version,
        "request_id": echoed_id,
        "status": status,
        "led": "green" if led == 0 else "blue",
        "accepted_count": count,
    }


def send_command(command, request_id, timeout=3.0):
    """Send once; timeouts/errors never fabricate an MCU response or retry."""
    result = {"request_id": request_id, "command": command}
    if any(type(value) is not int or not INT32_MIN <= value <= INT32_MAX
           for value in (command, request_id)):
        return {**result, "result": "client_error", "detail": "arguments must be int32"}
    if type(timeout) not in (int, float) or not 0 < timeout <= 10:
        return {**result, "result": "client_error", "detail": "timeout must be in (0, 10] seconds"}
    try:
        # Resolve only the real Arduino runtime, on the UNO Q Linux side.
        from arduino.app_utils import Bridge

        if "timeout" not in inspect.signature(Bridge.call).parameters:
            return {**result, "result": "communication_error", "delivery": "not_sent",
                    "error": "incompatible_api", "detail": "Bridge.call lacks timeout support"}
    except Exception as error:
        return {**result, "result": "communication_error", "delivery": "not_sent",
                "error": type(error).__name__, "detail": str(error)[:200]}
    try:
        reply = Bridge.call(METHOD, request_id, command, timeout=timeout)
    except Exception as error:
        return {**result, "result": "communication_error", "delivery": "unknown",
                "error": type(error).__name__, "detail": str(error)[:200]}
    try:
        acknowledgement = decode_ack(reply, request_id, command)
    except ValueError as error:
        return {**result, "result": "communication_error", "delivery": "unknown",
                "error": "invalid_ack", "detail": str(error)}
    status = acknowledgement["status"]
    return {**result, "result": "success" if status == 0 else "rejected",
            "reason": ("accepted", "unsupported_command", "invalid_request_id")[status],
            "ack": acknowledgement}
