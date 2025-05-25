from controllerTest import MotionControlResult, MotionControlTest
from controller import Controller

class RepeatabilityTest(MotionControlTest):

    def __init__(self, test_name: str, startPosn: float, endPosn: float, controller: Controller, errorMargin: float = 0.01, precision: float = 0.01, runs: int = 10):
        super().__init__(test_name, "Repeatability Test", controller)
        self.startPosn = startPosn
        self.endPosn = endPosn
        self.precision = precision
        self.runs = runs
        self.errorMargin = errorMargin

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = self.controller

        controller.move_to_pos_wait(motor, self.startPosn)
        
        run_results = []

        for i in range(self.runs):
            controller.move_to_pos_wait(motor, self.endPosn)
            final_pos = controller.get_pos(encoder)

            run_results.append(final_pos)

            controller.move_to_pos_wait(motor, self.startPosn)
        

        # Calculate the average final position
        average_final_pos = sum(run_results) / len(run_results)
        largest_deviation = max(abs(pos - self.endPosn) for pos in run_results)
        # Check if the average final position is within the precision range
        if abs(average_final_pos - self.endPosn) < self.precision and largest_deviation < self.errorMargin:
            message = f"Move test passed. Average final position: {average_final_pos}, Largest deviation: {largest_deviation}"
            result = MotionControlResult(success=True, message=message)
        else:
            message = f"Move test failed. Expected: Less than {self.precision}, Actual: {average_final_pos - self.endPosn} with largest deviation {largest_deviation}"
            result = MotionControlResult(success=False, message=message)


        controller.disconnect()
        return result