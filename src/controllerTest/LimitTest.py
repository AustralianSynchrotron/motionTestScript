from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time

class LimitTest(MotionControlTest):

    def __init__(self, test_name: str, controller: Controller):
            super().__init__(test_name, "Limit Test", controller)

    def execute(self, motor: int, encoder: int):
        #connect to the controller
        controller = self.controller
        st = time()
        
        #set speed to max speed
        max_speed = controller.get_maximum_velocity(motor)
        print(max_speed)
        controller.set_velocity(motor, max_speed)

        #back off in case it is on the switch already
        controller.move_by_relative_pos_wait(motor, 10)
        
        #move to positive end position
        #controller.set_velocity(motor, 0.001)
        controller.move_to_end_neg_wait(motor)
        negative_end_result = int(controller.send_receive_with_print(f"Motor[{motor}].MinusLimit"))
        
        #move to negative end position
        controller.move_to_end_pos_wait(motor)
        positive_end_result = int(controller.send_receive_with_print(f"Motor[{motor}].PlusLimit"))
        duration = time() - st
        #output the results
        print(f"Positive End Limit: {positive_end_result}")
        print(f"Negative End Limit: {negative_end_result}")

        success = positive_end_result and negative_end_result
        
        result = MotionControlResult(
            success=success,
            test_name=self.test_name,
            expected_value="Both limits should be reached",
            actual_value=f"Positive: {positive_end_result}, Negative: {negative_end_result}",
            duration=duration,  # Duration is not calculated in this test
            gathered_data={
                'positive_end_limit': positive_end_result,
                'negative_end_limit': negative_end_result
            }
        )

        return result