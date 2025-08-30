from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time

class MoveTestAbsolute(MotionControlTest):

    def __init__(self, test_name: str, posn_add: float, controller: Controller, precision: float = 0.01):
        super().__init__(test_name, "Relative Move Test", controller)
        self.posn_add = posn_add
        self.precision = precision

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = self.controller
        initial_pos = controller.get_pos(encoder)
        expected_pos = initial_pos + self.posn_add

        st = time()
        controller.move_to_pos_wait(motor, self.posn_add)
        final_pos = controller.get_pos(encoder)
        duration = time() - st

        success = abs(expected_pos - final_pos) < self.precision

        result = MotionControlResult(success=success,
                                     test_name=self.test_name, expected_value=self.posn_add,
                                     actual_value=final_pos-initial_pos, duration=duration)

        return result