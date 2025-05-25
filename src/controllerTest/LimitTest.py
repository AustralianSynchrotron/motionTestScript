from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
import time

class LimitTest(MotionControlTest):

    def __init__(self, test_name: str, controller: Controller):
            super().__init__(test_name, "Limit Test", controller)

    def execute(self, motor: int, encoder: int):
        #connect to the controller
        controller = self.controller
        
        #move to positive end position
        #controller.set_velocity(motor, 0.001)
        controller.move_to_end_neg_wait(motor)
        positive_end_result = int(controller.send_receive_with_print(f"Motor[{motor}].MinusLimit"))
        
        #move to negative end position
        controller.move_to_end_pos_wait(motor)
        negative_end_result = int(controller.send_receive_with_print(f"Motor[{motor}].PlusLimit"))
        
        #output the results
        print(f"Positive End Limit: {positive_end_result}")
        print(f"Negative End Limit: {negative_end_result}")

        if positive_end_result and negative_end_result:
             result = MotionControlResult(success=True, message="Limit test passed.")
        else:
             result = MotionControlResult(success=False, message="Limit test failed.")

        return result