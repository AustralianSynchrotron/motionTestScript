from controllerTest import MotionControlResult, MotionControlTest  # Base test class & result container
from controller import Controller  # Hardware controller abstraction
from time import time  # For simple duration timing

class MoveTestAbsolute(MotionControlTest):
    """Test that commands an absolute move and verifies final position accuracy.

    Success criterion: |final_position - target_position| < precision.
    """

    def __init__(self, test_name: str, posn: float, controller: Controller, precision: float = 0.01):
        super().__init__(test_name, "Absolute Move Test", controller)
        self.posn = posn            # Target absolute position to command
        self.precision = precision  # Allowed absolute error band

    def execute(self, motor: int, encoder: int):
        """Run the absolute move then evaluate position error against tolerance."""
        controller = self.controller
        initial_pos = controller.get_pos(encoder)  # Capture starting point (diagnostic)

        st = time()  # Start timing
        controller.move_to_pos_wait(motor, self.posn)  # Blocking absolute move
        final_pos = controller.get_pos(encoder)
        duration = time() - st  # Elapsed time for the motion

        # Determine pass/fail based on absolute error
        success = abs(final_pos - self.posn) < self.precision

        # Build result object (additional diagnostics could be added to gathered_data later)
        result = MotionControlResult(
            id=self.id,
            success=success,
            generic_name=self.generic_name,
            test_name=self.test_name,
            expected_value=f"Position {self.posn} +/- {self.precision}",
            actual_value=final_pos,
            duration=duration,
            extra_data={
                'initial_position': initial_pos,
                'target_position': self.posn,
                'final_position': final_pos,
                'position_error': final_pos - self.posn,
                'precision': self.precision
            }
        )
        return result