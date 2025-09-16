from controllerTest import MotionControlTest, MoveTestAbsolute, VelocityTest, LimitTest, RepeatabilityTest, OvershootTest, MotionControlResult
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

        controller.initialise(chan=motor)

        for test in tests_to_run(controller=controller):
            test_result = test.main_execution(motor, encoder, timeout, gather_data, gather_data_items)
            results.append(test_result)

        
        ReportGenerator(results).generate_report(f"motion_control_report_{run_id}.txt")

        controller.disconnect()

        # absMoveTestMacro = MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=-50, controller=controller,precision=0.001)
        # absMoveTestMacroResult = absMoveTestMacro.main_execution(motor, encoder, 60, True, ["IqCmd.a", "Pos.a"])
        # #absMoveTestMacroResult = absMoveTestMacro.execute(motor, encoder)
        # print(absMoveTestMacroResult)
        # results.append(absMoveTestMacroResult)

        #currentTest = CurrentGather("Current test", controller=controller)
        #currentTest.execute(motor=2,encoder=10)

        # limitTest = LimitTest(test_name="Limit Test", controller=controller)
        # limitTestResult = limitTest.main_execution(motor, encoder,120,True,["Pos.a", "Pos.a"])
        # print(limitTestResult)
        # results.append(limitTestResult)
        
        
        #limitTest = LimitTest(test_name="Limit Test", controller=controller)
        #id_this = "5bdd6e5f-0f3a-4983-b1cf-17d673dd488e"
        #limitTestResult = limitTest.visualise_gather_data(id_this, "move test absolute", f"{id}_graph_output2", ["Pos.a", "Pos.a"])

        """
        absMoveTestMicro = MoveTestAbsolute(test_name="Absolute Move Test Micro", posn=10.005, controller=controller, precision=0.001)
        absMoveTestMicroResult = absMoveTestMicro.execute(motor, encoder)
        #print(absMoveTestMicroResult)
        results.append(absMoveTestMicroResult)

        absMoveTestMacro = MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=15, controller=controller,precision=0.001)
        absMoveTestMacroResult = absMoveTestMacro.execute(motor, encoder)
        #print(absMoveTestMacroResult)
        results.append(absMoveTestMacroResult)

        absMoveTestMacroPrecise = MoveTestAbsolute(test_name="Absolute Move Test Macro Precise", posn=25.005, controller=controller, precision=0.001)
        absMoveTestMacroPreciseResult = absMoveTestMacroPrecise.execute(motor, encoder)
        #print(absMoveTestMacroPreciseResult)
        results.append(absMoveTestMacroPreciseResult)

        precisionTestMicro = RepeatabilityTest(test_name="Repeatability Test Micro", startPosn=10, endPosn=10.005, controller=controller, errorMargin=0.01, precision=0.001)
        precisionTestMicroResult = precisionTestMicro.execute(motor, encoder)
        #print(precisionTestMicroResult)
        results.append(precisionTestMicroResult)

        precisionTestMacro = RepeatabilityTest(test_name="Repeatability Test Macro", startPosn=10, endPosn=20, controller=controller, errorMargin=0.01, precision=0.001)
        precisionTestMacroResult = precisionTestMacro.execute(motor, encoder)
        #print(precisionTestMacroResult)
        results.append(precisionTestMacroResult)

        precisionTestMicroLarge = RepeatabilityTest(test_name="Repeatability Test Micro Large", startPosn=10, endPosn=20.005, controller=controller, errorMargin=0.01, precision=0.001)
        precisionTestMicroLargeResult = precisionTestMicroLarge.execute(motor, encoder)
        #print(precisionTestMicroLargeResult)
        results.append(precisionTestMicroLargeResult)

        limitTest = LimitTest(test_name="Limit Test", controller=controller)
        limitTestResult = limitTest.execute(motor, encoder)
        #print(limitTestResult)
        results.append(limitTestResult)

        overshootTestSlow = OvershootTest(test_name="Overshoot Test Slow", velocity=0.001, controller=controller, precision=0.001)
        overshootTestSlowResult = overshootTestSlow.execute(motor, encoder)
        #print(overshootTestSlowResult)
        results.append(overshootTestSlowResult)

        overshootTestMedium = OvershootTest(test_name="Overshoot Test Medium", velocity=0.0025, controller=controller, precision=0.001)
        overshootTestMediumResult = overshootTestMedium.execute(motor, encoder)
        #print(overshootTestMediumResult)
        results.append(overshootTestMediumResult)

        overshootTestFast = OvershootTest(test_name="Overshoot Test Fast", velocity=0.004, controller=controller, precision=0.001)
        overshootTestFastResult = overshootTestFast.execute(motor, encoder)
        #print(overshootTestFastResult)
        results.append(overshootTestFastResult)

        velocityTestSlow = VelocityTest(test_name="Velocity Test Slow", velocity=0.001, controller=controller, precision=0.001)
        velocityTestSlowResult = velocityTestSlow.execute(motor, encoder)
        #print(velocityTestSlowResult)
        results.append(velocityTestSlowResult)

        velocityTestMedium = VelocityTest(test_name="Velocity Test Medium", velocity=0.0025, controller=controller, precision=0.001)
        velocityTestMediumResult = velocityTestMedium.execute(motor, encoder)
        #print(velocityTestMediumResult)
        results.append(velocityTestMediumResult)

        velocityTestFast = VelocityTest(test_name="Velocity Test Fast", velocity=0.004, controller=controller, precision=0.001)
        velocityTestFastResult = velocityTestFast.execute(motor=1, encoder=9)
        print(velocityTestFastResult)
        """


        # # Example usage
        # print("Test 1")
        # test = MoveTestAbsolute(test_name="Test 1", posn=10.005, controller=controller, precision=0.00025)
        # result = test.execute(motor, encoder)

        # print("Test 2")
        # test2 = VelocityTest(test_name="Test 2", velocity = 0.004, controller=controller)
        # result2 = test2.execute(motor, encoder)

        # print("Test 3")
        # test3 = LimitTest(test_name="Limit Test", controller=controller)
        # result3 = test3.execute(motor, encoder)

        # print("Test 4")
        # test4 = PrecisionTest(test_name="Precision Test", startPosn=10, endPosn=15.005, controller=controller, precision=0.0001)
        # result4 = test4.execute(motor, encoder)

        # print(result)
        # print(result2)
        # print(result3)
        # print(result4)

        controller.disconnect()

    except KeyboardInterrupt:
        controller.graceful_exit(chan=1)
        controller.disconnect()

def tests_to_run(controller) -> List[MotionControlTest]:

    tests = []

    tests.append(MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=-50, controller=controller,precision=0.001))
    tests.append(LimitTest(test_name="Limit Test", controller=controller))                                                                                          

    return tests


if __name__ == "__main__":
    main()

    """
    controller = Controller(host="10.23.231.3")
    controller.connect()
    motor = 2
    encoder = 10

    intialised = controller.initialise(chan=motor)
    print(f"Controller initialised: {intialised}")
    """
    #absMoveTestMacro = MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=0, controller=controller,precision=0.001)
    #absMoveTestMacroResult = absMoveTestMacro.timeout_execution(motor, encoder, 2)
    #print(absMoveTestMacroResult)
    

    # Example usage:
    #results = [
    #    MotionControlResult(success=True, test_name="Move Test 1", expected_value=10.0, actual_value=10.0, duration=0.5),
    #    MotionControlResult(success=False, test_name="Move Test 2", expected_value=20.0, actual_value=19.5, duration=0.6, gathered_data={"current": [0.1, 0.2, 0.3], "volage": [1.0, 1.1, 1.2]})
    #]

    #report_generator = ReportGenerator(results)
    #report_generator.generate_report("motion_control_report.txt")