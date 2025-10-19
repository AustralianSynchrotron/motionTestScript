from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time

"""LimitTest

Verifies that both the negative and positive end limit switches for a motor can be
successfully reached (i.e. they report active once driven to each end). The test:
 1. Sets the jog velocity to the controller's maximum for the motor (fast traversal).
 2. Backs off a little to avoid starting already on a limit switch.
 3. Drives to the negative end until the controller helper method reports completion.
 4. Reads the negative limit status bit.
 5. Drives to the positive end and reads the positive limit status bit.
 6. Reports success only if both limit bits were seen active (non‑zero).

Safety / Assumptions:
 - get_maximum_velocity(motor) returns a safe velocity already configured in the system.
 - move_to_end_neg_wait / move_to_end_pos_wait block until motion/limit assertion completes.
 - Positive/Negative naming: "MinusLimit" corresponds to negative end, "PlusLimit" to positive end.
"""

class LimitTest(MotionControlTest):

    def __init__(self, test_name: str, controller: Controller):
            super().__init__(test_name, "Limit Test", controller)

    def execute(self, motor: int, encoder: int):
        # Reference to controller convenience
        controller = self.controller
        st = time()
        
        # 1. Set speed to maximum configured velocity (assumed safe)
        max_speed = controller.get_maximum_velocity(motor)
        print(max_speed)
        controller.set_velocity(motor, max_speed)

        # 2. Back off a small distance so we are not already sitting on a limit
        controller.move_by_relative_pos_wait(motor, 10)
        
        # 3. Drive to NEGATIVE end (method name indicates negative direction)
        controller.move_to_end_neg_wait(motor)
        negative_end_result = int(controller.send_receive_with_print(f"Motor[{motor}].MinusLimit"))
        
        # 4. Drive to POSITIVE end
        controller.move_to_end_pos_wait(motor)
        positive_end_result = int(controller.send_receive_with_print(f"Motor[{motor}].PlusLimit"))
        duration = time() - st
        # 5. Log results
        print(f"Positive End Limit: {positive_end_result}")
        print(f"Negative End Limit: {negative_end_result}")

        # 6. Success only if both limit bits were asserted (non-zero)
        success = bool(positive_end_result and negative_end_result)
        
        result = MotionControlResult(
            id=self.id,
            success=success,
            generic_name=self.generic_name,
            test_name=self.test_name,
            expected_value="Both limit switches must activate",
            actual_value=f"Positive: {bool(positive_end_result)}, Negative: {bool(negative_end_result)}",
            duration=duration,
            extra_data={
                'positive_limit_active': bool(positive_end_result),
                'negative_limit_active': bool(negative_end_result),
                'max_speed_used': max_speed
            }
        )

        return result