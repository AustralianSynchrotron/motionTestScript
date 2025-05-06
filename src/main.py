from controllerTest.MoveTestAbsolute import MoveTestAbsolute
from controllerTest.VelocityTest import VelocityTest
from controllerTest.LimitTest import LimitTest
from controllerTest.PrecisionTest import PrecisionTest

def main():
    """
    Main function to run the move test.
    """
    # Example usage
    print("Test 1")
    test = MoveTestAbsolute(test_name="Test 1", posn=10.005, precision=0.00025)
    result = test.execute(motor=1, encoder=9)

    print("Test 2")
    test2 = VelocityTest(test_name="Test 2", velocity = 0.004)
    result2 = test2.execute(motor=1, encoder=9)

    print("Test 3")
    test3 = LimitTest(test_name="Limit Test")
    result3 = test3.execute(motor=1, encoder=9)

    print("Test 4")
    test4 = PrecisionTest(test_name="Precision Test", startPosn=10, endPosn=15.005, precision=0.0001)
    result4 = test4.execute(motor=1, encoder=9)

    print(result)
    print(result2)
    print(result3)
    print(result4)

if __name__ == "__main__":
    main()