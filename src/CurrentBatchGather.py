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
    controller.move_to_pos_wait(chan=1, posn=0)
    controller.move_to_pos(chan=1, posn=20)

    results = controller.current_fetch_in_batch(chan=1)
    print(results)

    controller.disconnect()


except KeyboardInterrupt:
    controller.graceful_exit(chan=1)
    controller.disconnect()
