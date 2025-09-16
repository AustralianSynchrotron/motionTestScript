from controllerTest import MotionControlResult, MotionControlTest  # Base classes / result container
from controller import Controller  # Hardware controller abstraction
from time import time  # Simple timing
import statistics  # For standard deviation calculation

"""RepeatabilityTest

Exercises a point-to-point move multiple times to quantify positioning repeatability.

Metrics collected:
    - average_final_pos: mean of final encoder positions across runs
    - largest_deviation: max |final_pos - target| across runs
    - standard_deviation: dispersion of the final positions

Pass criteria (all must be satisfied):
    |average_final_pos - endPosn| < precision AND
    largest_deviation < errorMargin AND
    standard_deviation < max_std
"""

class RepeatabilityTest(MotionControlTest):

    def __init__(self, test_name: str, startPosn: float, endPosn: float, controller: Controller,
                 errorMargin: float = 0.01, max_std: float = 0.1, precision: float = 0.01, runs: int = 10):
        super().__init__(test_name, "Repeatability Test", controller)
        self.startPosn = startPosn       # Start location each cycle begins from
        self.endPosn = endPosn           # Target endpoint whose repeatability is assessed
        self.precision = precision       # Allowed mean error band vs target
        self.runs = runs                 # Number of repetitions
        self.errorMargin = errorMargin   # Max allowed single-run absolute deviation
        self.max_std = max_std           # Max allowed standard deviation across runs

    def execute(self, motor: int, encoder: int):
        """Perform repeated moves and evaluate positional repeatability."""
        controller = self.controller

        st = time()
        controller.move_to_pos_wait(motor, self.startPosn)  # Ensure known starting point

        run_results = []  # Collected final positions after each move to endPosn
        for i in range(self.runs):
            controller.move_to_pos_wait(motor, self.endPosn)
            final_pos = controller.get_pos(encoder)
            run_results.append(final_pos)
            controller.move_to_pos_wait(motor, self.startPosn)  # Return to start for next cycle

        duration = time() - st

        average_final_pos = sum(run_results) / len(run_results)
        standard_dev = statistics.stdev(run_results) if len(run_results) > 1 else 0.0
        largest_deviation = max(abs(pos - self.endPosn) for pos in run_results)

        success = (
            abs(average_final_pos - self.endPosn) < self.precision and
            largest_deviation < self.errorMargin and
            standard_dev < self.max_std
        )

        result = MotionControlResult(
            id=self.id,
            success=success,
            test_name=self.test_name,
            expected_value=self.endPosn,
            actual_value=average_final_pos,
            duration=duration,
            gathered_data={
                'average_final_pos': average_final_pos,
                'largest_deviation': largest_deviation,
                'standard_deviation': standard_dev,
                'runs': run_results
            }
        )
        return result