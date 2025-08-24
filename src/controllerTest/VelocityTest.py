from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time, sleep

class VelocityTest(MotionControlTest):

    def __init__(self, test_name: str, velocity: float, controller: Controller, precision: float = 0.0002):
        super().__init__(test_name, "Velocity Test", controller)
        self.velocity = velocity
        self.precision = precision

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = self.controller
        
        st = time()
        controller.move_to_end_pos_wait(motor)
        controller.set_velocity(motor, self.velocity)
        controller.move_to_end_neg(motor)
        sleep(2)
        vol = controller.get_velocity(encoder)
        duration = time() - st


        success = abs(vol) - abs(self.velocity) < self.precision
        result = MotionControlResult(
            success=success,
            test_name=self.test_name,
            expected_value=f"Velocity should be within {self.precision} of {self.velocity}",
            actual_value=vol,
            duration=duration,  # Duration is not calculated in this test
            gathered_data={
                'velocity': vol
            }
        )

        return result