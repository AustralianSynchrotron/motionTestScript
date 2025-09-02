from abc import ABC, abstractmethod
from controller import Controller
import time
import concurrent.futures
from controllerTest.MotionControlResult import MotionControlResult
import uuid
import numpy as np
import matplotlib.pyplot as plt
import threading
import pandas as pd

class MotionControlTest(ABC):
    """
    Abstract base class for motion control tests.
    """

    def __init__(self, test_name: str, generic_name: str, controller: Controller):
        self.id = str(uuid.uuid4())
        self.test_name = test_name
        self.generic_name = generic_name
        self.controller = controller

    def main_execution(self, motor: int, encoder: int, timeout: float = 60.0, gather_data: bool = False, measure_item: list = None):
        """
        Execute the test with a timeout.
        """

        if gather_data:
            print("Starting data gather...")
            thread = threading.Thread(target=self.controller.start_gather, args=(motor, self.id, measure_item))
            thread.start()
            time.sleep(1)
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.execute, motor, encoder)
            print("executing test...")
            try:
                # Wait until execute() completes or the timeout is reached.
                result = future.result(timeout=timeout)
                elapsed = time.time() - start_time
                print(f"Test '{self.test_name}' completed in {elapsed:.2f} seconds.")
            except concurrent.futures.TimeoutError:
                elapsed = time.time() - start_time
                print(f"Test '{self.test_name}' timed out after {elapsed:.2f} seconds.")
                # Attempt to stop current command, if supported.
                self.controller.graceful_exit(motor)
                # Return a failed MotionControlResult.
                result = MotionControlResult(
                    success=False,
                    test_name=self.test_name,
                    expected_value=None,
                    actual_value=None,
                    duration=elapsed
                )
            finally:
                if gather_data:
                    print("Ending data gather...")
                    self.controller.end_gather(self.id)
                    
                    self.visualise_gather_data(self.id, self.test_name, f"{self.id}_graph_output", measure_item)
                return result

    def visualise_gather_data(self, id, title, path, meas_item):
        
        #read data
        df = pd.read_csv(f"gather_output_{id}.txt", delim_whitespace=True, header=None)
        if len(df.columns) != len(meas_item):
           raise ValueError(f"Expected {len(meas_item)} columns, got {len(df.columns)}")
        df.columns = meas_item
        

        if len(meas_item) > 1:
           data = tuple(df[col] for col in df.columns)
        else:
            data = tuple(df)

        if data is None:
            return None
        
        times = np.arange(len(data[0]))
        fig = plt.figure()
        for i in range(len(data)):
            subplot = fig.add_subplot(len(data), 1, i+1)
    
            subplot.plot(times, data[i], label=str(data[i]))
            #labels
            subplot.set_xlabel("Timestep")
            # Y label from measure_item
            ylabel = meas_item[i]
            subplot.set_ylabel(ylabel)
            if title:
                subplot.set_title(title)
            subplot.legend(meas_item[i])

        fig.savefig(path)
        plt.close(fig)
        
    

    @abstractmethod
    def execute(self, motor: int, encoder: int):
        """
        Run the motion control test.
        """
        pass