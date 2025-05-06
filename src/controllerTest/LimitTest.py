from controllerTest.MotionControlResult import MotionControlResult
from controllerTest.MotionControlTest import MotionControlTest
from controller import Controller
import time

class LimitTest(MotionControlTest):

    def __init__(self, test_name: str, velocity: float, precision: float = 0.0002):
            super().__init__(test_name)

    def execute(self, motor: int, encoder: int):
        #connect to the controller
        controller = Controller(host="10.23.231.3")
        controller.connect()
        
        #move to positive end position
        controller.set_velocity(motor, 0.013)
        controller.move_to_end_pos_wait(motor)
        positive_end_result = controller.send_receive_with_print(f"Gate1[0].Chan[{motor - 1}].MinusLimit")
        
        #move to negative end position
        controller.move_to_end_pos_wait(motor)
        negative_end_result = controller.send_receive_with_print(f"Gate1[0].Chan[{motor - 1}].PlusLimit")
        
        #output the results
        print(f"Positive End Limit: {positive_end_result}")
        print(f"Negative End Limit: {negative_end_result}")