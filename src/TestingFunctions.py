from controller import Controller

try:
    controller = Controller(host="10.23.231.3")
    controller.connect()
    for i in range(1, 10):
        currents = controller.current_fetch(chan=1)
        print(currents)
    
except KeyboardInterrupt:
    controller.graceful_exit(chan=1)
    controller.disconnect()