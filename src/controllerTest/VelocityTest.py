from controllerTest.MotionControlResult import MotionControlResult
from controllerTest.MotionControlTest import MotionControlTest
from controller import Controller
import time

class VelocityTest(MotionControlTest):

    def __init__(self, test_name: str, velocity: float, precision: float = 0.001):
        super().__init__(test_name)
        self.velocity = velocity
        self.precision = precision

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = Controller(host="10.23.231.3")
        controller.connect()
        
        controller.move_to_end_pos_wait(motor)
        controller.move_to_end_neg(motor)
        time.sleep(1)
        vol = controller.get_velocity(encoder)


        

        if abs(vol - self.velocity) < self.precision:
            result = MotionControlResult(success=True, message="Velocity test passed.")
        else:
            message = f"Velocity test failed. Expected: {self.velocity}, Actual: {vol}"
            result = MotionControlResult(success=False, message=message)

        controller.wait_till_done(motor)
        controller.disconnect()
        return result