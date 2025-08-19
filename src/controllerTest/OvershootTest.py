from .MotionControlTest import MotionControlTest
from .MotionControlResult import MotionControlResult
from controller import Controller
import time

class OvershootTest(MotionControlTest):

    def __init__(self, test_name: str, velocity: float, controller: Controller, distance: float = 10, precision: float = 0.001):
            super().__init__(test_name, "Overshoot Test")
            self.precision = precision
            self.distance = distance
            self.velocity = velocity
            self.controller = controller

    def execute(self, motor: int, encoder: int):
        #connect to the controller
        controller = self.controller
        
        controller.set_velocity(motor, self.velocity)
        #start moving
        controller.move_to_pos(motor, self.distance)
        peak_position = 0
        inpos_state = controller.in_pos(motor)
        controller.start_gather(chan=motor, max_sample=5000, meas_item=["IaMeas.a", "IbMeas.a"])
        while (inpos_state) != 1:
            pos = controller.get_pos(encoder)
            peak_position = max(peak_position, pos)
            inpos_state =  controller.in_pos(motor)
            #time.sleep(0.05)
        # calculate the overshoot
        overshoot = peak_position - self.distance
        
        #move back to 0 position
        controller.move_to_pos_wait(motor, 0)
        
        
        #check if the overshoot is within the precision
        if overshoot > self.precision:
            result = MotionControlResult(success=False, message=f"Overshoot test failed at speed {self.velocity}. Overshoot: {overshoot}")
        else:
            result = MotionControlResult(success=True, message=f"Overshoot test passed at speed {self.velocity}. Overshoot: {overshoot}")
                
        return result
        
            
     