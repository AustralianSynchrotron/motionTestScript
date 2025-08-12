from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time

class MoveTestAbsolute(MotionControlTest):

    def __init__(self, test_name: str, posn: float, controller: Controller, precision: float = 0.01):
        super().__init__(test_name, "Absolute Move Test", controller)
        self.posn = posn
        self.precision = precision

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = self.controller
        initial_pos = controller.get_pos(encoder)

        st = time()
        controller.move_to_pos_wait(motor, self.posn)
        final_pos = controller.get_pos(encoder)
        duration = time() - st

        success = abs(final_pos - self.posn) < self.precision

        result = MotionControlResult(success=success,
                                     test_name=self.test_name, expected_value=self.posn,
                                     actual_value=final_pos, duration=duration)

        controller.disconnect()
        return result