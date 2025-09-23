from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time

"""Relative move verification test.

How it works:
 1. Read the starting encoder position (initial_pos).
 2. Compute the expected final position as initial_pos + posn_add.
 3. Command a move using move_to_pos_wait with 'posn_add'. 
 4. After motion completes, read the final encoder position.
 5. Compare the achieved displacement (final_pos vs expected_pos) against the
     configured precision tolerance -> pass/fail.
 6. Report the actual relative displacement (final_pos - initial_pos) in the result.

Fields:
  posn_add  : Intended relative increment.
  precision : Maximum allowed absolute error between expected and final position.
"""

class MoveTestRelative(MotionControlTest):

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
        controller.move_to_pos_relative_wait(motor, self.posn_add)
        final_pos = controller.get_pos(encoder)
        duration = time() - st

        success = abs(expected_pos - final_pos) < self.precision

        result = MotionControlResult(
            id=self.id,
            success=success,
            generic_name=self.generic_name,
            test_name=self.test_name,
            expected_value=f"Relative move of {self.posn_add} ± {self.precision}",
            actual_value=final_pos - initial_pos,
            duration=duration,
            extra_data={
                'initial_position': initial_pos,
                'final_position': final_pos,
                'target_displacement': self.posn_add,
                'actual_displacement': final_pos - initial_pos
            }
        )
        return result