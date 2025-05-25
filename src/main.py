from controllerTest import MoveTestAbsolute, VelocityTest, LimitTest, RepeatabilityTest, OvershootTest
from controller import Controller

def main():
    """
    Main function to run the move test.
    """

    try:

        controller = Controller(host="10.23.231.3")
        controller.connect()

        absMoveTestMicro = MoveTestAbsolute(test_name="Absolute Move Test Micro", posn=10.005, controller=controller, precision=0.001)
        absMoveTestMicroResult = absMoveTestMicro.execute(motor=1, encoder=9)
        print(absMoveTestMicroResult)

        absMoveTestMacro = MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=15, controller=controller,precision=0.001)
        absMoveTestMacroResult = absMoveTestMacro.execute(motor=1, encoder=9)
        print(absMoveTestMacroResult)

        absMoveTestMacroPrecise = MoveTestAbsolute(test_name="Absolute Move Test Macro Precise", posn=25.005, controller=controller, precision=0.001)
        absMoveTestMacroPreciseResult = absMoveTestMacroPrecise.execute(motor=1, encoder=9)
        print(absMoveTestMacroPreciseResult)

        precisionTestMicro = RepeatabilityTest(test_name="Repeatability Test Micro", startPosn=10, endPosn=10.005, controller=controller, errorMargin=0.01, precision=0.001)
        precisionTestMicroResult = precisionTestMicro.execute(motor=1, encoder=9)
        print(precisionTestMicroResult)

        precisionTestMacro = RepeatabilityTest(test_name="Repeatability Test Macro", startPosn=10, endPosn=20, controller=controller, errorMargin=0.01, precision=0.001)
        precisionTestMacroResult = precisionTestMacro.execute(motor=1, encoder=9)
        print(precisionTestMacroResult)

        precisionTestMicroLarge = RepeatabilityTest(test_name="Repeatability Test Micro Large", startPosn=10, endPosn=20.005, controller=controller, errorMargin=0.01, precision=0.001)
        precisionTestMicroLargeResult = precisionTestMicroLarge.execute(motor=1, encoder=9)
        print(precisionTestMicroLargeResult)

        limitTest = LimitTest(test_name="Limit Test", controller=controller)
        limitTestResult = limitTest.execute(motor=1, encoder=9)
        print(limitTestResult)

        overshootTestSlow = OvershootTest(test_name="Overshoot Test Slow", velocity=0.001, controller=controller, precision=0.001)
        overshootTestSlowResult = overshootTestSlow.execute(motor=1, encoder=9)
        print(overshootTestSlowResult)

        overshootTestMedium = OvershootTest(test_name="Overshoot Test Medium", velocity=0.0025, controller=controller, precision=0.001)
        overshootTestMediumResult = overshootTestMedium.execute(motor=1, encoder=9)
        print(overshootTestMediumResult)

        overshootTestFast = OvershootTest(test_name="Overshoot Test Fast", velocity=0.004, controller=controller, precision=0.001)
        overshootTestFastResult = overshootTestFast.execute(motor=1, encoder=9)
        print(overshootTestFastResult)

        velocityTestSlow = VelocityTest(test_name="Velocity Test Slow", velocity=0.001, controller=controller, precision=0.001)
        velocityTestSlowResult = velocityTestSlow.execute(motor=1, encoder=9)
        print(velocityTestSlowResult)

        velocityTestMedium = VelocityTest(test_name="Velocity Test Medium", velocity=0.0025, controller=controller, precision=0.001)
        velocityTestMediumResult = velocityTestMedium.execute(motor=1, encoder=9)
        print(velocityTestMediumResult)

        velocityTestFast = VelocityTest(test_name="Velocity Test Fast", velocity=0.004, controller=controller, precision=0.001)
        velocityTestFastResult = velocityTestFast.execute(motor=1, encoder=9)
        print(velocityTestFastResult)



        # # Example usage
        # print("Test 1")
        # test = MoveTestAbsolute(test_name="Test 1", posn=10.005, controller=controller, precision=0.00025)
        # result = test.execute(motor=1, encoder=9)

        # print("Test 2")
        # test2 = VelocityTest(test_name="Test 2", velocity = 0.004, controller=controller)
        # result2 = test2.execute(motor=1, encoder=9)

        # print("Test 3")
        # test3 = LimitTest(test_name="Limit Test", controller=controller)
        # result3 = test3.execute(motor=1, encoder=9)

        # print("Test 4")
        # test4 = PrecisionTest(test_name="Precision Test", startPosn=10, endPosn=15.005, controller=controller, precision=0.0001)
        # result4 = test4.execute(motor=1, encoder=9)

        # print(result)
        # print(result2)
        # print(result3)
        # print(result4)

        controller.disconnect()

    except KeyboardInterrupt:
        controller.graceful_exit(chan=1)
        controller.disconnect()


if __name__ == "__main__":
    main()