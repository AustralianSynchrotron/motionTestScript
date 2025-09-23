"""VelocityTest

Executes a unidirectional move intended to run the motor at a configured velocity, then
gathers actual velocity samples and compares their average to the target velocity.

Process:
 1. Move to positive end position (ensures sufficient travel distance available going negative).
 2. Program the commanded velocity.
 3. Issue a move toward the negative end (continuous move helper).
 4. Wait a short settling period (fixed 2 s).
 5. Gather a block of actual velocity samples and average them.
 6. Pass if averaged |actual| is within precision of |commanded| (see note below).

Note: Success check uses (abs(actual) - abs(commanded)) < precision; if actual < commanded this is
negative (auto-pass). A stricter absolute difference would be abs(abs(actual) - abs(commanded)).
Left unchanged intentionally—documenting current behavior only.
"""

from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time, sleep

class VelocityTest(MotionControlTest):
    """Average measured velocity vs target velocity within tolerance."""

    def __init__(self, test_name: str, velocity: float, controller: Controller, precision: float = 0.0002):
        super().__init__(test_name, "Velocity Test", controller)
        self.velocity = velocity      # Commanded velocity to compare against
        self.precision = precision    # Allowed difference (see note in module docstring)

    def execute(self, motor: int, encoder: int):
        """Run velocity check and return MotionControlResult."""

        controller = self.controller

        st = time()  # (Duration not currently used, kept for parity with other tests.)
        controller.move_to_end_pos_wait(motor)  # Ensure we have full travel in the negative direction
        controller.set_velocity(motor, self.velocity)  # Program target velocity
        controller.move_to_end_neg(motor)  # Begin moving negative
        time.sleep(2)  # Allow motion to stabilize before sampling

        # Gather actual velocity samples (ActVel) and average them.
        controller.start_gather(chan=motor, max_sample=5000, meas_item=[f"Motor[{motor}].ActVel"])
        vol = controller.end_gather(
            save_to_filename="velocity_output.txt",
            meas_item=[f"Motor[{motor}].ActVel"],
            as_tuple=False
        )
        vol = sum(vol) / len(vol)  # Average over samples
        # Alternative (instant) approach was: controller.get_velocity(encoder)

        success = abs(vol) - abs(self.velocity) < self.precision  # See note in module docstring
        result = MotionControlResult(
            id=self.id,
            success=success,
            generic_name=self.generic_name,
            test_name=self.test_name,
            expected_value=f"{self.velocity} ± {self.precision}",
            actual_value=vol,
            duration=time() - st,  # Use actual duration instead of "N/A"
            extra_data={
                'target_velocity': self.velocity,
                'measured_velocity': vol,
                'precision': self.precision
            }
        )
        return result