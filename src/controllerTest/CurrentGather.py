from controller import Controller
from controllerTest import MotionControlResult, MotionControlTest
import matplotlib.pyplot as plt
import numpy as np
import threading
import time

class CurrentGather(MotionControlTest):
    def __init__(self, test_name: str, controller: Controller):
        super().__init__(test_name, "Current Test", controller)

    def execute(self, motor: int, encoder:int):
        """
        Run the current test.
        """
        #initialisation
        controller = self.controller

        controller.move_to_end_neg_wait(chan=motor)

        # Start gather
        thread = threading.Thread(target=controller.start_gather, args=(motor, 2000, ["IqCmd.a"]))
        thread.start()

        time.sleep(5)
        # Move robot
        controller.move_to_pos_wait(chan=motor, posn=10)
        # End gather
        i_a = controller.end_gather(save_to_filename = "current_output.txt",meas_item=["IqCmd.a"],as_tuple=False)
        #i_a = i_a[0]
        print(len(i_a))
        print(type(i_a))
        print(i_a[0:100])
        # Plot the data
        times = np.linspace(0,len(i_a),len(i_a))
        plt.plot(times, i_a)
        #plt.plot(i_b, label="Ib")
        plt.show()

        controller.disconnect()



