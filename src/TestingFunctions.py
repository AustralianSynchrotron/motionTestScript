from controller import Controller
import time
import matplotlib.pyplot as plt
import numpy as np


try:
    #initialisation
    controller = Controller(host="10.23.231.3")
    controller.connect()
    time_step = 0.01
    times = np.arange(0,3,time_step)
    currents = []

    #move
    controller.move_to_pos(chan=1, posn=-20)

    for i in range(len(times)):
        current = controller.current_fetch(chan=1)
        currents.append(current)
        print(current)
        time.sleep(0.01)

    controller.disconnect()

    #plotting
    print(len(currents))
    print(len(times))
    plt.plot(times, currents)
    plt.title("Current(A) aginst time")
    plt.xlabel("Time in " + str(time_step) + " second steps")
    plt.ylabel("Current in A")
    plt.show()
    
    
except KeyboardInterrupt:
    controller.graceful_exit(chan=1)
    controller.disconnect()




