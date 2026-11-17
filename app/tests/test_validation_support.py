"""No database or model required: failure signaling and hung-worker regression checks."""
import threading
import unittest

from validation_support import run_concurrently, suite_exit_code


class ValidationSupportTests(unittest.TestCase):
    def test_failure_and_blocked_status_are_not_success(self):
        self.assertEqual(suite_exit_code([{"outcome": "Pass"}, {"outcome": "Info"}]), 0)
        self.assertEqual(suite_exit_code([{"outcome": "Fail"}, {"outcome": "Pass"}]), 1)
        self.assertEqual(suite_exit_code([{"outcome": "Blocked"}]), 2)
        self.assertEqual(suite_exit_code([{"outcome": "Blocked"}, {"outcome": "Fail"}]), 1)

    def test_concurrent_exceptions_are_reported(self):
        def fail():
            raise ValueError("invalid operation")
        self.assertEqual(run_concurrently([lambda: None, fail], str), ["ok", "invalid operation"])

    def test_hung_worker_has_a_deadline(self):
        release = threading.Event()
        try:
            with self.assertRaises(TimeoutError):
                run_concurrently([release.wait], str, timeout=0.05)
        finally:
            release.set()


if __name__ == "__main__":
    unittest.main()
