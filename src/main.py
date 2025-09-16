from controllerTest import MotionControlTest, MoveTestAbsolute, VelocityTest, LimitTest, RepeatabilityTest, OvershootTest, MoveTestRelative, MotionControlResult
from controller import Controller
from report import ReportGenerator
from typing import List

def main():
    """
    Main function to run the move test.
    """

    try:
        host_ip = "10.23.231.3"
        controller = Controller(host=host_ip)
        controller.connect()
        results = []
        motor = 2
        encoder = 10
        gather_data = True
        gather_data_items = ["IqCmd.a", "Pos.a"]
        timeout = 120
        run_id = "test_run_001"

        controller.initialise(chan=motor, enc=encoder)

        for test in tests_to_run(controller=controller):
            test_result = test.main_execution(motor, encoder, timeout, gather_data, gather_data_items)
            results.append(test_result)

        
        ReportGenerator(results).generate_report(f"results/motion_control_report_{run_id}.txt")

        controller.custom_command_blocking(chan=2, cmd="#chanj=2")

        controller.disconnect()

    except KeyboardInterrupt:
        controller.graceful_exit(chan=1)
        controller.disconnect()

def tests_to_run(controller) -> List[MotionControlTest]:

    tests = []

    tests.append(MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=-50, controller=controller,precision=0.001))
    tests.append(LimitTest(test_name="Limit Test", controller=controller))      
    tests.append(MoveTestRelative(test_name="Relative Move Test Macro", posn_add=20, controller=controller, precision=0.001))   
    tests.append(RepeatabilityTest(test_name="Repeatability Test", startPosn=10, endPosn=20, controller=controller, errorMargin=0.01, precision=0.001, runs=5))                                                                                 

    return tests


if __name__ == "__main__":
    main()