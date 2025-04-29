from controllerTest.MoveTestAbsolute import MoveTestAbsolute
from controllerTest.VelocityTest import VelocityTest

def main():
    """
    Main function to run the move test.
    """
    # Example usage
    test = MoveTestAbsolute(test_name="Test 1", posn=10.0, precision=0.01)
    result = test.execute(motor=1, encoder=9)

    test2 = VelocityTest(test_name = "Test 2", velocity = 0.0005)
    result2 = test2.execute(motor=1, encoder=9)

    print(result)
    print(result2)

if __name__ == "__main__":
    main()