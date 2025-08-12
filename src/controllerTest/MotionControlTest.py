from abc import ABC, abstractmethod
from controller import Controller
import time
import concurrent.futures
from controllerTest import MotionControlResult

class MotionControlTest(ABC):
    """
    Abstract base class for motion control tests.
    """

    def __init__(self, test_name: str, generic_name: str, controller: Controller):
        self.test_name = test_name
        self.generic_name = generic_name
        self.controller = controller

    def timeout_execution(self, motor: int, encoder: int, timeout: float = 60.0):
        """
        Execute the test with a timeout.
        """
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.execute, motor, encoder)
            try:
                # Wait until execute() completes or the timeout is reached.
                result = future.result(timeout=timeout)
                elapsed = time.time() - start_time
                print(f"Test '{self.test_name}' completed in {elapsed:.2f} seconds.")
                return result
            except concurrent.futures.TimeoutError:
                elapsed = time.time() - start_time
                print(f"Test '{self.test_name}' timed out after {elapsed:.2f} seconds.")
                # Attempt to stop current command, if supported.
                self.controller.graceful_exit(motor)
                # Return a failed MotionControlResult.
                return MotionControlResult(
                    success=False,
                    test_name=self.test_name,
                    expected_value=None,
                    actual_value=None,
                    duration=elapsed
                )

    @abstractmethod
    def execute(self, motor: int, encoder: int):
        """
        Run the motion control test.
        """
        pass