from controllerTest import MoveTestAbsolute, VelocityTest, LimitTest, PrecisionTest
from controller import Controller

def main():
    """
    Main function to run the move test.
    """

    try:

        controller = Controller(host="10.23.231.3")
        controller.connect()

        absMoveTestMicro = MoveTestAbsolute(test_name="Absolute Move Test Micro", posn=10.005, controller=controller, precision=0.00025)
        absMoveTestMicroResult = absMoveTestMicro.execute(motor=1, encoder=9)
        print(absMoveTestMicroResult)

        absMoveTestMacro = MoveTestAbsolute(test_name="Absolute Move Test Macro", posn=15, controller=controller,precision=0.00025)
        absMoveTestMacroResult = absMoveTestMacro.execute(motor=1, encoder=9)
        print(absMoveTestMacroResult)

        absMoveTestMacroPrecise = MoveTestAbsolute(test_name="Absolute Move Test Macro Precise", posn=25.005, controller=controller, precision=0.00025)
        absMoveTestMacroPreciseResult = absMoveTestMacroPrecise.execute(motor=1, encoder=9)
        print(absMoveTestMacroPreciseResult)

        precisionTestMicro = PrecisionTest(test_name="Precision Test Micro", startPosn=10, endPosn=10.005, controller=controller, precision=0.00025)
        precisionTestMicroResult = precisionTestMicro.execute(motor=1, encoder=9)
        print(precisionTestMicroResult)

        precisionTestMacro = PrecisionTest(test_name="Precision Test Macro", startPosn=10, endPosn=20, controller=controller, precision=0.00025)
        precisionTestMacroResult = precisionTestMacro.execute(motor=1, encoder=9)
        print(precisionTestMacroResult)

        precisionTestMicroLarge = PrecisionTest(test_name="Precision Test Micro Large", startPosn=10, endPosn=20.005, controller=controller, precision=0.00025)
        precisionTestMicroLargeResult = precisionTestMicroLarge.execute(motor=1, encoder=9)
        print(precisionTestMicroLargeResult)

        # Example usage
        print("Test 1")
        test = MoveTestAbsolute(test_name="Test 1", posn=10.005, controller=controller, precision=0.00025)
        result = test.execute(motor=1, encoder=9)

        print("Test 2")
        test2 = VelocityTest(test_name="Test 2", velocity = 0.004, controller=controller)
        result2 = test2.execute(motor=1, encoder=9)

        print("Test 3")
        test3 = LimitTest(test_name="Limit Test", controller=controller)
        result3 = test3.execute(motor=1, encoder=9)

        print("Test 4")
        test4 = PrecisionTest(test_name="Precision Test", startPosn=10, endPosn=15.005, controller=controller, precision=0.0001)
        result4 = test4.execute(motor=1, encoder=9)

        print(result)
        print(result2)
        print(result3)
        print(result4)

        controller.disconnect()

    except KeyboardInterrupt:
        controller.graceful_exit(chan=1)
        controller.disconnect()


if __name__ == "__main__":
    main()