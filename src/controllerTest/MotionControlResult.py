
class MotionControlResult:
    """
    Class to represent the result of a motion control operation.
    """

    def __init__(self, id: str, success: bool, test_name: str,
                 expected_value, actual_value, duration: float = None,
                 gathered_data: dict = None):
        self.success = success

        self.id = id
        self.test_name = test_name
        self.expected_value = expected_value
        self.actual_value = actual_value
        self.duration = duration
        self.gathered_data = gathered_data if gathered_data is not None else {}

    def __str__(self):
        return (f"MotionControlResult(test_name='{self.test_name}', success={self.success}, "
                f"expected_value={self.expected_value}, actual_value={self.actual_value}, "
                f"duration={self.duration}, gathered_data={self.gathered_data})")