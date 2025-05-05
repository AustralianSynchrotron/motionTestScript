from controllerTest.MotionControlResult import MotionControlResult
from controllerTest.MotionControlTest import MotionControlTest
from controller import Controller

class PrecisionTest(MotionControlTest):

    def __init__(self, test_name: str, startPosn: float, endPosn: float, precision: float = 0.01, runs: int = 10):
        super().__init__(test_name)
        self.startPosn = startPosn
        self.endPosn = endPosn
        self.precision = precision
        self.runs = runs

    def execute(self, motor: int, encoder: int):
        """
        Run the move test.
        """

        controller = Controller(host="10.23.231.3")
        controller.connect()

        controller.move_to_pos_wait(motor, self.startPosn)
        
        run_results = []

        for i in range(self.runs):
            controller.move_to_pos_wait(motor, self.endPosn)
            final_pos = controller.get_pos(encoder)

            run_results.append(final_pos)

            controller.move_to_pos_wait(motor, self.startPosn)
        

        # Calculate the average final position
        average_final_pos = sum(run_results) / len(run_results)
        # Check if the average final position is within the precision range
        if abs(average_final_pos - self.endPosn) < self.precision:
            result = MotionControlResult(success=True, message="Move test passed.")
        else:
            message = f"Move test failed. Expected: Less than {self.precision}, Actual: {average_final_pos - self.endPosn}"
            result = MotionControlResult(success=False, message=message)


        controller.disconnect()
        return result