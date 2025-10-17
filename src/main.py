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
        timeout = 300
        run_id = "test_run_002"

        controller.initialise(chan=motor, enc=encoder)

        for test in tests_to_run(controller=controller):
            test_result = test.main_execution(motor, encoder, timeout, gather_data, gather_data_items)
            results.append(test_result)

        
        ReportGenerator(results).generate_report(f"results/motion_control_report_{run_id}.txt")

        controller.disconnect()

    except KeyboardInterrupt:
        controller.graceful_exit(chan=motor)
        controller.disconnect()

def tests_to_run(controller) -> List[MotionControlTest]:

    tests = []

    # Asbolute Move Tests
    tests.append(MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=-50, controller=controller,precision=0.001))
    tests.append(MoveTestAbsolute(test_name="Absolute Move Test Micro", posn=-49.005, controller=controller, precision=0.001))
    tests.append(MoveTestAbsolute(test_name="Absolute Move Test Macro Precise", posn=25.005, controller=controller, precision=0.001))

    # Relative Move Tests
    tests.append(MoveTestRelative(test_name="Relative Move Test Macro", posn_add=-50, controller=controller,precision=0.001))
    tests.append(MoveTestRelative(test_name="Relative Move Test Micro", posn_add=0.005, controller=controller, precision=0.001))
    tests.append(MoveTestRelative(test_name="Relative Move Test Macro Precise", posn_add=25.005, controller=controller, precision=0.001))
    
    # Repeatability Tests
    tests.append(RepeatabilityTest(test_name="Repeatability Test Micro", startPosn=10, endPosn=10.005, controller=controller, errorMargin=0.01, max_std=0.1, precision=0.001, runs=5))
    tests.append(RepeatabilityTest(test_name="Repeatability Test Macro", startPosn=10, endPosn=20, controller=controller, errorMargin=0.01, max_std=0.1, precision=0.001, runs=5))
    tests.append(RepeatabilityTest(test_name="Repeatability Test Micro Large", startPosn=0, endPosn=20.005, controller=controller, errorMargin=0.01, max_std=0.1, precision=0.001, runs=5))

    # Overshoot Tests
    tests.append(OvershootTest(test_name="Overshoot Test Slow", velocity=0.001, controller=controller, precision=0.001, distance=10))
    tests.append(OvershootTest(test_name="Overshoot Test Medium", velocity=0.0025, controller=controller, precision=0.001, distance=10))
    tests.append(OvershootTest(test_name="Overshoot Test Fast", velocity=0.005, controller=controller, precision=0.001, distance=10))
    
    # Velocity Tests
    tests.append(VelocityTest(test_name="Velocity Test Slow", velocity=0.001, controller=controller, precision=0.0001))
    tests.append(VelocityTest(test_name="Velocity Test Medium", velocity=0.0025, controller=controller, precision=0.0001))
    tests.append(VelocityTest(test_name="Velocity Test Fast", velocity=0.004, controller=controller, precision=0.0001))

    # Limit Test
    tests.append(LimitTest(test_name="Limit Test", controller=controller))                                                                             

    return tests


if __name__ == "__main__":
    main()