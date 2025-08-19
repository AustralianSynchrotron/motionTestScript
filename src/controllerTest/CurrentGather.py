from controller import Controller
import matplotlib.pyplot as plt
import numpy as np

class CurrentGather:
    def __init__(self, test_name: str, controller: Controller):
        super().__init__(test_name, "Current Test", controller)

def execute(self, chan: int):
    """
    Run the current test.
    """
    #initialisation
    controller = self.controller

    controller.move_to_end_neg_wait(chan=chan)

    # Start gather
    controller.start_gather(chan=chan, max_sample=2000, meas_item=["IaMeas.a", "IbMeas.a"])
    # Move robot
    controller.move_to_end_pos_wait(chan=chan)
    # End gather
    i_a, i_b = controller.end_gather(save_to_filename = "current_output.txt",meas_item=["IaMeas.a", "IbMeas.a"],as_tuple=True)

    # Plot the data
    plt.plot(i_a, label="Ia")
    plt.plot(i_b, label="Ib")
    plt.legend()
    plt.show()

    controller.disconnect()



