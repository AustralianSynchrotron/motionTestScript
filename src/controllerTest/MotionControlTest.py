from abc import ABC, abstractmethod  # For defining the abstract base class / method contract
from controller import Controller
import time
import concurrent.futures  # Used to enforce a timeout around the concrete test execution
from controllerTest.MotionControlResult import MotionControlResult
import uuid  # Generates a unique id per test instance (used for gather file naming, result tracking)
import numpy as np
import matplotlib.pyplot as plt
import threading  # Allows starting the gather in a background thread so test timing isn't delayed
import pandas as pd

class MotionControlTest(ABC):
    """Abstract base class / template for motion control tests.

    Subclasses implement `execute` containing the specific motion sequence and
    validation logic. This base class handles:
      - Unique test id creation
      - Optional Power PMAC data gather start/end and plotting
      - Timeout management so a stalled move doesn't block the suite
      - Standard result object construction (delegated to subclass inside execute)
    """

    def __init__(self, test_name: str, generic_name: str, controller: Controller):
        # Unique id so gather output & plots don't collide between runs.
        self.id = str(uuid.uuid4())
        self.test_name = test_name
        self.generic_name = generic_name
        self.controller = controller

    def main_execution(self, motor: int, encoder: int, timeout: float = 60.0, gather_data: bool = False, measure_item: list = None):
        """Run the concrete test with optional gather + timeout wrapper.

        Parameters:
            motor:        Motor index used for motion commands.
            encoder:      Encoder index (passed to execute; some tests may ignore it).
            timeout:      Maximum seconds to wait for `execute` to finish.
            gather_data:  If True, start controller gather before running execute.
            measure_item: List of variable names corresponding to gather columns.
        """

        if gather_data:
            print("Starting data gather...")
            thread = threading.Thread(target=self.controller.start_gather, args=(motor, self.id, measure_item))
            thread.start()
            time.sleep(1)  # Brief delay so initial samples are captured before motion starts.

        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:  # Single worker to isolate this test
            future = executor.submit(self.execute, motor, encoder)
            print("executing test...")
            try:
                # Wait until execute() completes or the timeout is reached.
                result = future.result(timeout=timeout)
                elapsed = time.time() - start_time
                print(f"Test '{self.test_name}' completed in {elapsed:.2f} seconds.")
            except Exception:
                elapsed = time.time() - start_time
                print(f"Test '{self.test_name}' timed out after {elapsed:.2f} seconds.")
                # Attempt to stop current command, if supported.
                self.controller.graceful_exit(motor)
                # Return a failed MotionControlResult.
                result = MotionControlResult(
                    id=self.id,
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
                    # Plot gathered signals (PNG saved using test id prefix)
                    self.visualise_gather_data(self.id, self.test_name, f"results/{self.id}_graph_output", measure_item)
                return result

    def visualise_gather_data(self, id, title, path, meas_item):
        """Read the gather output file and create one subplot per measured item.

        Assumes:
          - Gather produces space-delimited columns with no header.
          - Servo period is 0.5 ms (sample rate 2000 Hz) so time = index / 2000.
        """

        # Read raw gather file (space separated values)
        df = pd.read_csv(f"results/gather_output_{id}.txt", delim_whitespace=True, header=None)
        if len(df.columns) != len(meas_item):
            raise ValueError(f"Expected {len(meas_item)} columns, got {len(df.columns)}")
        df.columns = meas_item
        # Build time axis in seconds (0.5 ms per sample)
        times = np.arange(len(df)) / 2000  # 0.5 ms per sample => seconds

        # Create subplots (one per variable); keep axes iterable for single case
        fig, axes = plt.subplots(len(meas_item), 1, figsize=(10, 5 * len(meas_item)))
        if len(meas_item) == 1:
            axes = [axes]
        for i, ax in enumerate(axes):
            ax.plot(times, df[meas_item[i]], label=meas_item[i])
            if len(times):
                max_t = times[-1]
                second_ticks = np.arange(0, max_t + 1, 1)
                ax.set_xticks(second_ticks)
            # Axis labels
            ax.set_xlabel("Times (s)")
            ylabel = meas_item[i]
            ax.set_ylabel(ylabel)
            if title:
                ax.set_title(title)
            ax.legend()

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig(path)
        plt.close(fig)

    @abstractmethod
    def execute(self, motor: int, encoder: int):
        """Concrete test logic implemented by subclasses.

        Should perform motion operations and return a MotionControlResult.
        """
        pass