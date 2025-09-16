from .MotionControlTest import MotionControlTest          # Base test template
from .MotionControlResult import MotionControlResult      # Result container
from controller import Controller                         # Hardware controller abstraction
from time import time                                     # Timing for duration

"""Overshoot measurement test.

Purpose:
    Command a move to a target distance and capture the maximum position reached
    during the motion. Overshoot is (peak_position - target_distance). Test passes
    if overshoot <= precision.

Notes:
    - Uses a non-blocking move_to_pos then polls in-position while tracking peak.
    - A gather is started for phase currents (Ia/Ib) but never explicitly stopped
        here (end_gather should be invoked externally if needed).
    - For a stricter measurement you might also sample position at servo rate via
        gather, rather than using polling.
"""

class OvershootTest(MotionControlTest):

    def __init__(self, test_name: str, velocity: float, controller: Controller, distance: float = 10, precision: float = 0.001):
        super().__init__(test_name, "Overshoot Test", controller)
        self.precision = precision   # Allowed overshoot (units)
        self.distance = distance     # Target absolute position
        self.velocity = velocity     # Commanded velocity for move
        self.controller = controller

    def execute(self, motor: int, encoder: int):
        """Run overshoot evaluation.

        Steps:
          1. Set velocity.
          2. Command non-blocking move to target distance.
          3. Poll position until in-position while tracking peak.
          4. Compute overshoot and return to zero.
          5. Pass if overshoot <= precision.
        """
        controller = self.controller

        controller.set_velocity(motor, self.velocity)
        st = time()
        controller.move_to_pos(motor, self.distance)  # Non-blocking move
        peak_position = 0
        inpos_state = controller.in_pos(motor)
        controller.start_gather(chan=motor, max_sample=5000, meas_item=["IaMeas.a", "IbMeas.a"])  # Current gather
        while inpos_state != 1:
            pos = controller.get_pos(encoder)
            peak_position = max(peak_position, pos)
            inpos_state = controller.in_pos(motor)
            # Optional small sleep could reduce CPU usage
        duration = time() - st

        overshoot = peak_position - self.distance

        # Return to origin (baseline) after measurement
        controller.move_to_pos_wait(motor, 0)

        success = overshoot <= self.precision

        result = MotionControlResult(
            id=self.id,
            success=success,
            test_name=self.test_name,
            expected_value="<= " + str(self.precision),
            actual_value=overshoot,
            duration=duration
        )
        return result
        
            
     