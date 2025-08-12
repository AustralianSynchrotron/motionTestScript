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
    #controller.move_to_pos_wait(chan=2, posn=0)
    #controller.move_to_pos(chan=2, posn=20)

    controller.current_fetch_in_batch(chan=2)
    #print(Ia,Ib)

    controller.disconnect()


except KeyboardInterrupt:
    controller.graceful_exit(chan=2)
    controller.disconnect()
