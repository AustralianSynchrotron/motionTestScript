from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller
from time import time
import statistics

class RepeatabilityTest(MotionControlTest):

    def __init__(self, test_name: str, startPosn: float, endPosn: float, controller: Controller, errorMargin: float = 0.01, max_std: float = 0.1, precision: float = 0.01, runs: int = 10):
        super().__init__(test_name, "Repeatability Test", controller)
        self.startPosn = startPosn
        self.endPosn = endPosn
        self.precision = precision
        self.runs = runs
        self.errorMargin = errorMargin
        self.max_std = max_std

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = self.controller

        st = time()
        controller.move_to_pos_wait(motor, self.startPosn)
        
        run_results = []

        for i in range(self.runs):
            controller.move_to_pos_wait(motor, self.endPosn)
            final_pos = controller.get_pos(encoder)

            run_results.append(final_pos)

            controller.move_to_pos_wait(motor, self.startPosn)
        duration = time() - st

        # Calculate the average final position
        average_final_pos = sum(run_results) / len(run_results)
        standard_dev = statistics.stdev(run_results) if len(run_results) > 1 else 0.0
        largest_deviation = max(abs(pos - self.endPosn) for pos in run_results)
        # Check if the average final position is within the precision range
        success = abs(average_final_pos - self.endPosn) < self.precision and largest_deviation < self.errorMargin and standard_dev < self.max_std

        result = MotionControlResult(
            success=success,
            test_name=self.test_name,
            expected_value=self.endPosn,
            actual_value=average_final_pos,
            duration=duration,  # Duration is not calculated in this test
            gathered_data={
                'average_final_pos': average_final_pos,
                'largest_deviation': largest_deviation,
                'standard_deviation': standard_dev,
                'runs': run_results
            }
        )
        
        return result