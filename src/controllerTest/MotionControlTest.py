from abc import ABC, abstractmethod
from controller import Controller
import time
import concurrent.futures
from controllerTest.MotionControlResult import MotionControlResult
import uuid
import numpy as np
import matplotlib.pyplot as plt

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
            self.controller.start_gather(chan=motor, test_id=self.id, meas_item=measure_item)
        
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
                    #self.visualise_gather_data(gathered_data, self.test_name, f"{self.id}_output.txt", measure_item)
                return result

    def visualise_gather_data(self, data, title, path, measure_item):
    
        if data is None:
            return None
        times = np.arange(len(data))
        fig = plt.figure()
        for col in data.columns:
            plt.plot(times, data[col], label=str(col))
        #labels
        plt.xlabel("Timestep")
        # Y label from measure_item
        if measure_item:
            ylabel = measure_item[0] if len(measure_item) == 1 else "Value (" + ", ".join(measure_item) + ")"
        else:
            ylabel = "Value" if len(data.columns) > 1 else str(data.columns[0])
        plt.ylabel(ylabel)
        if title:
            plt.title(title)
        plt.legend()
        fig.savefig(path)
        plt.close(fig)
        
    

    @abstractmethod
    def execute(self, motor: int, encoder: int):
        """
        Run the motion control test.
        """
        pass