from controller import Controller
import time
import matplotlib.pyplot as plt
import numpy as np


try:
    #initialisation
    controller = Controller(host="10.23.231.3")
    controller.connect()
    time_period = 3
    time_step = 0.01
    time_array = np.arange(0, time_period, time_step)

    #move
    #reset postion
    controller.move_to_pos_wait(chan=1, posn=0)
    #move the stage
    controller.move_to_pos(chan=1, posn=20)

    currents = controller.current_fetch(chan=1, time_period=time_period, time_step=time_step)
    print(currents)

    controller.disconnect()

    #plotting
    print(len(currents))
    print(len(time_array))
    plt.plot(time_array, currents)
    plt.title("Current(A) aginst time")
    plt.xlabel("Time in " + str(time_step) + " second steps")
    plt.ylabel("Current in A")
    plt.show()
    
    
except KeyboardInterrupt:
    controller.graceful_exit(chan=1)
    controller.disconnect()




