from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
import time

class VelocityTest(MotionControlTest):

    def __init__(self, test_name: str, velocity: float, precision: float = 0.0002):
        super().__init__(test_name, "Velocity Test")
        self.velocity = velocity
        self.precision = precision

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = Controller(host="10.23.231.3")
        controller.connect()
        
        controller.move_to_end_pos_wait(motor)
        controller.set_velocity(motor, self.velocity)
        controller.move_to_end_neg(motor)
        time.sleep(2)
        vol = controller.get_velocity(encoder)


        

        if abs(vol) - abs(self.velocity) < self.precision:
            result = MotionControlResult(success=True, message="Velocity test passed.")
        else:
            message = f"Velocity test failed. Expected: {self.velocity}, Actual: {vol}"
            result = MotionControlResult(success=False, message=message)

        controller.wait_till_done(motor)
        controller.disconnect()
        return result