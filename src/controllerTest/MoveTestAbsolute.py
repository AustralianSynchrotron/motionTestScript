from controllerTest.MotionControlResult import MotionControlResult
from controllerTest.MotionControlTest import MotionControlTest
from controller import Controller

class MoveTestAbsolute(MotionControlTest):

    def __init__(self, test_name: str, posn: float, precision: float = 0.01):
        super().__init__(test_name, "Absolute Move Test")
        self.posn = posn
        self.precision = precision

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = Controller(host="10.23.231.3")
        controller.connect()
        initial_pos = controller.get_pos(encoder)

        controller.move_to_pos_wait(motor, self.posn)

        final_pos = controller.get_pos(encoder)

        if abs(final_pos - self.posn) < self.precision:
            result = MotionControlResult(success=True, message="Move test passed.")
        else:
            message = f"Move test failed. Expected: {self.posn}, Actual: {final_pos}"
            result = MotionControlResult(success=False, message=message)

        controller.disconnect()
        return result