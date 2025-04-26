
class MotionControlResult:
    """
    Class to represent the result of a motion control operation.
    """

    def __init__(self, success: bool, message: str):
        """
        Initialize the MotionControlResult.

        :param success: Indicates if the motion control operation was successful.
        :param message: A message providing additional information about the result.
        """
        self.success = success
        self.message = message

    def __str__(self):
        return f"MotionControlResult(success={self.success}, message='{self.message}')"