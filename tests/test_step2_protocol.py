"""Offline contract checks using synthetic acknowledgements only.

These tests exercise the Python protocol decoder and local argument guards.
They do not import Arduino modules, call Bridge, or simulate MCU responses.
"""

import unittest

from apps.step2.python.rpc_client import decode_ack, send_command


class OfflineSyntheticProtocolFixtures(unittest.TestCase):
    """Pure Python checks; acknowledgement arrays below are synthetic fixtures."""

    def test_accepts_green_and_blue_acknowledgements(self):
        green = decode_ack([1, 17, 0, 0, 1], 17, 0)
        blue = decode_ack((1, 18, 0, 1, 3), 18, 1)

        self.assertEqual(green["led"], "green")
        self.assertEqual(green["accepted_count"], 1)
        self.assertEqual(blue["led"], "blue")
        self.assertEqual(blue["accepted_count"], 3)

    def test_accepts_unsupported_command_rejection(self):
        ack = decode_ack([1, 19, 1, 1, 0], 19, 99)
        self.assertEqual(ack["status"], 1)

    def test_accepts_nonpositive_request_id_rejection(self):
        ack = decode_ack([1, 0, 2, 0, 0], 0, 0)
        self.assertEqual(ack["status"], 2)

    def test_rejects_wrong_schema(self):
        for reply in (None, {}, "1,2,3,4,5", [1, 2, 0, 0], [1, 2, 0, 0, 1, 6]):
            with self.subTest(reply=reply), self.assertRaises(ValueError):
                decode_ack(reply, 2, 0)

    def test_rejects_wrong_version_id_and_status(self):
        invalid = (
            ([2, 17, 0, 0, 1], 17, 0),
            ([1, 18, 0, 0, 1], 17, 0),
            ([1, 17, 1, 0, 0], 17, 0),
            ([1, 17, 0, 0, 0], 17, 0),
            ([1, 17, 0, 1, 1], 17, 0),
            ([1, 17, 2, 0, 0], 17, 99),
        )
        for reply, request_id, command in invalid:
            with self.subTest(reply=reply, command=command), self.assertRaises(ValueError):
                decode_ack(reply, request_id, command)

    def test_rejects_invalid_led_and_count(self):
        invalid = (
            [1, 17, 0, 2, 1],
            [1, 17, 0, -1, 1],
            [1, 17, 0, 0, -1],
            [1, 17, 0, 0, 0],
        )
        for reply in invalid:
            with self.subTest(reply=reply), self.assertRaises(ValueError):
                decode_ack(reply, 17, 0)

    def test_rejects_non_integer_fields_including_booleans(self):
        for index in range(5):
            for bad_value in (True, False, 1.0, "1", None):
                reply = [1, 17, 0, 0, 1]
                reply[index] = bad_value
                with self.subTest(index=index, bad_value=bad_value), self.assertRaises(ValueError):
                    decode_ack(reply, 17, 0)

    def test_accepts_signed_int32_field_edges_when_contract_allows_them(self):
        # An unsupported command and rejected request ID can be represented at
        # the wire's signed-int32 boundaries; accepted counts remain nonnegative.
        self.assertEqual(decode_ack([1, 2_147_483_647, 1, 0, 0], 2_147_483_647, 2)["status"], 1)
        self.assertEqual(decode_ack([1, -2_147_483_648, 2, 0, 0], -2_147_483_648, 0)["status"], 2)
        self.assertEqual(decode_ack([1, 17, 0, 0, 2_147_483_647], 17, 0)["accepted_count"], 2_147_483_647)

    def test_rejects_int32_overflow_on_every_wire_field(self):
        baseline = [1, 17, 0, 0, 1]
        for index in range(5):
            for out_of_range in (-2_147_483_649, 2_147_483_648):
                reply = baseline.copy()
                reply[index] = out_of_range
                with self.subTest(index=index, value=out_of_range), self.assertRaises(ValueError):
                    decode_ack(reply, 17, 0)

    def test_send_command_rejects_invalid_local_arguments_without_runtime(self):
        invalid_arguments = (
            (True, 1, 3.0),
            (0, False, 3.0),
            (2_147_483_648, 1, 3.0),
            (-2_147_483_649, 1, 3.0),
            (0, 2_147_483_648, 3.0),
            (0, -2_147_483_649, 3.0),
            (0, 1, 0),
            (0, 1, 10.01),
            (0, 1, True),
            (0, 1, float("nan")),
        )
        for command, request_id, timeout in invalid_arguments:
            with self.subTest(command=command, request_id=request_id, timeout=timeout):
                result = send_command(command, request_id, timeout)
                self.assertEqual(result["result"], "client_error")


if __name__ == "__main__":
    unittest.main()
