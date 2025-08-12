from typing import List
from controllerTest import MotionControlResult

class ReportGenerator:

    def __init__(self, motion_control_results: List[MotionControlResult]):
        self.motion_control_results = motion_control_results


    def generate_report(self, path) -> None:
        with open(path, 'w') as report_file:
            report_file.write("Motion Control Test Report\n")
            report_file.write("==========================\n\n")
            for result in self.motion_control_results:
                report_file.write(f"Test Name: {result.test_name}\n")
                report_file.write(f"Success: {result.success}\n")
                report_file.write(f"Expected Value: {result.expected_value}\n")
                report_file.write(f"Actual Value: {result.actual_value}\n")
                report_file.write(f"Test Duration: {result.duration:.3f} seconds\n")
                report_file.write(f"Gathered Data: {result.gathered_data}\n")
                report_file.write("-------------------------------\n")
            report_file.write("End of Report\n")
        print(f"Report generated at {path}")

# Example usage:
results = [
    MotionControlResult(success=True, test_name="Move Test 1", expected_value=10.0, actual_value=10.0, duration=0.5),
    MotionControlResult(success=False, test_name="Move Test 2", expected_value=20.0, actual_value=19.5, duration=0.6, gathered_data={"current": [0.1, 0.2, 0.3]})
]

report_generator = ReportGenerator(results)
report_generator.generate_report("motion_control_report.txt")