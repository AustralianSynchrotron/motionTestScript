from .MotionControlTest import MotionControlTest
from .MotionControlResult import MotionControlResult
from controller import Controller
import time

class OvershootTest(MotionControlTest):

    def __init__(self, test_name: str, precision: float = 0.001, distance: float = 10):
            super().__init__(test_name, "Overshoot Test")
            self.precision = precision
            self.distance = distance

    def execute(self, motor: int, encoder: int):
        #connect to the controller
        controller = Controller(host="10.23.231.3")
        controller.connect()
        
        #variables
        speeds = {'slow': 0.001, 'medium': 0.0025, 'fast': 0.005}
        
        #move to 0 position
        controller.move_to_pos_wait(motor, 0)
        
        #loop through different speeds
        for speed in speeds:
            #set the speed
            controller.set_velocity(motor, speeds[speed])
            #start moving
            controller.move_to_pos(motor, self.distance)
            peak_position = 0
            inpos_state = controller.in_pos(motor)
            while (inpos_state) != 1:
                pos = controller.get_pos(encoder)
                peak_position = max(peak_position, pos)
                inpos_state =  controller.in_pos(motor)
                #time.sleep(0.05)
            # calculate the overshoot
            overshoot = peak_position - self.distance
            print(f"Speed: {speed}, Overshoot: {overshoot}")
            
            #move back to 0 position
            controller.move_to_pos_wait(motor, 0)
            
            
            #check if the overshoot is within the precision
            if overshoot > self.precision:
                print(f"Overshoot test failed at speed {speed}. Overshoot: {overshoot}")
                result = MotionControlResult(success=False, message=f"Overshoot test failed at speed {speed}. Overshoot: {overshoot}")
                return result
                
            else:
                print(f"Overshoot test passed at speed {speed}. Overshoot: {overshoot}")
                result = MotionControlResult(success=True, message=f"Overshoot test passed at speed {speed}. Overshoot: {overshoot}")
                
        return result
        
            
     