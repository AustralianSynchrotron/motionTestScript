"""Lightweight container for the outcome of a motion control test.

Fields:
    id            : Unique identifier (e.g. UUID) tying results, plots, gather files.
    success       : Boolean pass/fail outcome determined by the test logic.
    test_name     : Human readable test instance name.
    expected_value: Target value / condition (type kept generic).
    actual_value  : Observed value / measurement collected by the test.
    duration      : Execution time in seconds (optional; may be None).
    gathered_data : Dict for auxiliary data (statistics, traces, metadata).

Design notes:
 - Kept deliberately simple for easy serialization (e.g. JSON, report files).
 - Additional per test artifacts can be placed inside gathered_data without
   modifying the public API.
"""


class MotionControlResult:
    """Represents the result of a motion control operation / test case."""

    def __init__(self, id: str, success: bool, generic_name: str, test_name: str,
                 expected_value, actual_value, duration: float = None,
                 extra_data: dict = None):
        # Core outcome flag
        self.success = success

        # Identification / naming
        self.id = id                 # Unique id (often a UUID) linking files & plots
        self.test_name = test_name   # Human-readable label for reports/logs
        self.generic_name = generic_name  # Generic test type name (e.g. "Absolute Move Test")

        # Expectation vs observation
        self.expected_value = expected_value
        self.actual_value = actual_value

        # Timing (seconds)
        self.duration = duration

        # Arbitrary extra data (statistics, arrays, etc.)
        self.extra_data = extra_data if extra_data is not None else {}

    def __str__(self):
        return (
            f"MotionControlResult(test_name='{self.test_name}', success={self.success}, "
            f"expected_value={self.expected_value}, actual_value={self.actual_value}, "
            f"duration={self.duration}, gathered_data={self.extra_data})"
        )