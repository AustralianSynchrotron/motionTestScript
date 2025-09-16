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
        time.sleep(2)
        controller.start_gather(chan=motor, max_sample=5000, meas_item=[f"Motor[{motor}].ActVel"])
        vol = controller.end_gather(save_to_filename="velocity_output.txt", meas_item=[f"Motor[{motor}].ActVel"], as_tuple=False)
        vol = sum(vol)/ len(vol)  # Average the velocity over the samples
        #vol = controller.get_velocity(encoder)


        

        success = abs(vol) - abs(self.velocity) < self.precision
        result = MotionControlResult(
            id=self.id,
            success=success,
            test_name=self.test_name,
            expected_value=f"Velocity should be within {self.precision} of {self.velocity}",
            actual_value=vol,
            duration="N/A",  # Duration is not calculated in this test
            gathered_data={
                'velocity': vol
            }
        )

        return result